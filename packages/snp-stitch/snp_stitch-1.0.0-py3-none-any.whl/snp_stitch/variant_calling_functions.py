# I/O, feature extraction functions
import pysam 
from math import log
import numpy as np
import pandas as pd
import warnings 
from collections import defaultdict
import os
import joblib
import datetime

# TODO
# ^ also check what's going on with min quality, I seemed confused by that in comments
# check what's up with features, where are observed freqs getting used
# check if min freq arg is actually doing anything


def make_ref_base_dict(reference_fasta):
    ref_dict = {}
    fasta = pysam.FastaFile(reference_fasta)
    for ref in fasta.references:
        full_seq = fasta.fetch(ref)
        ref_dict[ref] = full_seq
    return ref_dict

def get_tnc(sequence):
    # gets the tnc per position for reference sequence
    tnc_dict = {}
    for pos in range(len(sequence)):
        if pos == 0:
            tnc = 'N'+sequence[:pos+2]
        elif pos == len(sequence)-1:
            tnc = sequence[pos-1:] + 'N'
        else:
            tnc = sequence[pos-1:pos+2]
        tnc_dict[pos] = tnc
    return tnc_dict

def get_hp(ref_sequence,window_size=61,hp_size_cutoff=4):
    # should we try this for upstream/downstream specific?
    # should return a dict of window_center:hp_percent
    # needs to use start as the middle of a window instead of calculating after the fact
    window_vals  = {} 
    half_window = int(round((window_size-1)/2,0))
    for focal in range(len(ref_sequence)):
        if focal-half_window >= 0:
            # catch start edge cases - end is fine, if upper ind > len then just goes to the end
            # this will not give IndexError if left to it's own devices, it just uses the negative index
            chunk = ref_sequence[focal-half_window:focal+half_window]
        else:
            chunk = ref_sequence[:focal+half_window]
        
        last_base = None
        hp_size = 1
        running_total = 0
        for base in chunk:
            if last_base is not None:
                if base == last_base:
                    hp_size += 1
                    last_base=base
                else:
                    # break in homopolymer run
                    if hp_size >= hp_size_cutoff:
                        running_total = running_total + hp_size
                    
                    hp_size = 1
                    last_base = base
            else:
                last_base = base
        # get hp ended on last base
        if hp_size >= hp_size_cutoff:
            running_total = running_total + hp_size
        # changed to chunk size because of end cases where chunk is < window size
        # problem is probably here, using chunk size but haven't changed window key 
        window_vals[focal] = running_total/len(chunk)
        
    return window_vals


def calculate_SOR(ref_fw, ref_rev, alt_fw, alt_rev):
    # avoids zero division errors
    ref_fw = ref_fw + 1
    ref_rev = ref_rev + 1
    alt_fw = alt_fw + 1
    alt_rev = alt_rev + 1

    symm_ratio  = (ref_fw*alt_rev)/(alt_fw*ref_rev) + (alt_fw*ref_rev)/(ref_fw*alt_rev)
    ref_ratio = min([ref_fw,ref_rev])/max([ref_fw,ref_rev])
    alt_ratio = min([alt_fw,alt_rev])/max([alt_fw,alt_rev])
    SOR = log(symm_ratio) + log(ref_ratio) - log(alt_ratio)

    return SOR
 

def normalise_without_nans(x):
    x_filt = x[x!=-1]
    return (x-x_filt.mean())/ x_filt.std()


# Variant calling functions
def prep_ref_seq_features(ref_fasta):
    print('Calculating features for reference sequence...')
    exp_seq_dict = make_ref_base_dict(ref_fasta)
    ref_name = list(exp_seq_dict.keys())[0]
    print('Getting TNC info...')
    tnc_dict = get_tnc([x for x in exp_seq_dict.values()][0])
    print('Getting homopolymer info...')
    hp_dict = get_hp([x for x in exp_seq_dict.values()][0])
    return (ref_name,tnc_dict,hp_dict)

def get_data_for_predict(bam_path,tnc_dict,hp_dict,feature_list):
    base_dict = defaultdict(dict)
    bamfile = pysam.AlignmentFile(bam_path,'rb',)
    print(f'Getting per-site features for file {bam_path}...')
    # still need to get the quality values for post-filtering
    for pileupcolumn in bamfile.pileup(max_depth=50000):
        ref_pos = pileupcolumn.reference_pos
        dir_dict = {'A':[0,0],'T':[0,0],'G':[0,0],'C':[0,0]}
        base_list_at_pos = [x.alignment.query_sequence[x.query_position] for x in pileupcolumn.pileups if not x.is_del and not x.is_refskip]
        try:
            base_dict[ref_pos]['freqs_A'] = base_list_at_pos.count('A')/len(base_list_at_pos)
            base_dict[ref_pos]['freqs_T'] = base_list_at_pos.count('T')/len(base_list_at_pos)
            base_dict[ref_pos]['freqs_C'] = base_list_at_pos.count('C')/len(base_list_at_pos)
            base_dict[ref_pos]['freqs_G'] = base_list_at_pos.count('G')/len(base_list_at_pos)
            for pread,qual in zip(pileupcolumn.pileups,pileupcolumn.get_query_qualities()):
                if pread.is_del or pread.is_refskip:
                    continue
                base = pread.alignment.query_sequence[pread.query_position]
                if not pread.alignment.is_reverse:
                    dir_dict[base][0] += 1
                elif pread.alignment.is_reverse:
                    dir_dict[base][1] += 1

                if 'quals' not in base_dict[ref_pos].keys():
                    base_dict[ref_pos]['quals'] = defaultdict(list)    
                base_dict[ref_pos]['quals'][base].append(qual)
            for base in 'ATGC':
                # low/zero freq bases marked with mean quality = 0
                if not base_dict[ref_pos]['quals'][base]:
                    base_dict[ref_pos][f'quals_{base}'] = 0
                elif len(base_dict[ref_pos]['quals'][base]) <= 20:
                    base_dict[ref_pos][f'quals_{base}'] = 0
                else:
                    base_dict[ref_pos][f'quals_{base}'] = np.mean(base_dict[ref_pos]['quals'][base])
            try:
                tnc = tnc_dict[ref_pos]
                base_dict[ref_pos]['tnc'] = tnc
                # this might be completely unnecessary, can't remember if I padded ends
                # it is, ends are e.g. NGG
                if len(tnc) == 3:
                    base_dict[ref_pos]['ref_base'] = tnc[1]
                elif ref_pos == 0:
                    base_dict[ref_pos]['ref_base'] = tnc[0]
                else:
                    base_dict[ref_pos]['ref_base'] = tnc[1]

            except KeyError:
                warnings.warn(f'A position with no tnc assigned? Position {ref_pos}')
                base_dict[ref_pos]['tnc'] = None
            try:
                base_dict[ref_pos]['hp_content'] = hp_dict[ref_pos]
            except KeyError:
                warnings.warn(f'A position with no hp content assigned? Position {ref_pos}')
                base_dict[ref_pos]['hp_content'] = None
            base_dict[ref_pos]['depth'] = pileupcolumn.nsegments

        except ZeroDivisionError:
            
            # I think a low coverage warning and don't include the position is fine, can't really say shit about it
            warnings.warn(f'No reads mapping at position {ref_pos}, it will not be included')
            continue

        ref = base_dict[ref_pos]['ref_base']
        for base in dir_dict:
            sor = calculate_SOR(dir_dict[ref][0],dir_dict[ref][1],dir_dict[base][0],dir_dict[base][1])
            base_dict[ref_pos][f'sb_{base}'] = sor
        
    df = pd.DataFrame.from_dict(base_dict,orient='index')
    df.dropna(inplace=True)
    features = df[feature_list]
    targets = df[['freqs_A','freqs_T','freqs_G','freqs_C']]
    return (features,targets,df)

def predict_test_data(new_features, model, label_encoders):
    # maybe some other debug stuff also needs to come out
    cat_cols = new_features.select_dtypes(include=['object']).columns
    cat_vals = pd.DataFrame(index=new_features.index)
    for col in cat_cols:
        cat_vals[col] = label_encoders[col].fit_transform(new_features[col])
        
    num_cols = new_features.select_dtypes(exclude=['object']).columns
    # num_vals = new_features.select_dtypes(exclude=['object']).apply(normalise_without_nans, axis=0)
    num_vals = new_features.select_dtypes(exclude=['object'])
    new_features_transformed = pd.concat([pd.DataFrame(num_vals,index=cat_vals.index), cat_vals], axis=1).values
    new_features_transformed = pd.DataFrame(new_features_transformed,columns=[*num_cols,*cat_cols])
    predicted_freqs = pd.DataFrame(model.predict(new_features_transformed))
    predicted_freqs = predicted_freqs.div(predicted_freqs.sum(axis=1), axis=0)
    return (new_features_transformed,predicted_freqs)

def get_variant_sites(test_bam,tnc_dict,hp_dict,tolerance,model_and_encoder_dir,sb_cutoff=1.5,qual_cutoff=20):
    model_and_encoders = os.listdir(model_and_encoder_dir)
    try:
        trained_model_file = [file for file in model_and_encoders if 'regressor' in file][0]
    except IndexError:
        print(f'No model found in specified dir: {model_and_encoder_dir}, model file name should contain "regressor" and encoder filenames should contain "encoder"')
        raise
    with open(os.path.join(model_and_encoder_dir,trained_model_file),'rb') as model_file:
        trained_model = joblib.load(model_file)
        print('Model loaded')
        label_encoders = {}
        for filename in model_and_encoders:
            if 'encoder' in filename:
                encoder = joblib.load(os.path.join(model_and_encoder_dir,filename))
                feature = filename.replace('_encoder.pkl','')
                label_encoders[feature] = encoder
        feature_list = [ 'hp_content',
                          'depth',
                          'tnc',
                          'ref_base']
        new_features, true_frequencies, full_data = get_data_for_predict(test_bam,tnc_dict,hp_dict,feature_list=feature_list)
        print('bam processed')
        ref_bases = new_features['ref_base']
        transformed_data,pred_frequencies = predict_test_data(new_features,trained_model,label_encoders)
        print('Allele frequencies predicted, calling variants...')
        base_order = [x[-1] for x in true_frequencies.columns]
        var_sites =  []
        for reference_position,(t,p,r) in enumerate(zip(true_frequencies.values,pred_frequencies.values,ref_bases)):
            for base, base_t, base_p in zip(base_order,t,p):
                diff = base_t - base_p 
                if diff > tolerance and base != r:
                    # frequency more than tol over predicted value for non-ref base
                    site_info = full_data.iloc[reference_position]
                    real_pos = int(site_info.name) + 1
                    SB = site_info[f'sb_{base}']
                    depth = site_info['depth']
                    try:
                        mean_base_quality = site_info[f'quals_{base}']
                    except KeyError:
                        
                        mean_base_quality = 21
                    if SB < sb_cutoff and mean_base_quality > qual_cutoff:
                        print(f'Position {real_pos} appears to be variant, {r} to {base}; predicted and true frequencies: {base_p}, {base_t}')
                        # print(new_features.iloc[reference_position])
                        # non reference base more than  <tolerance> higher than predicted value
                        # should include some info like the AF and predicted AF? Anything else? Prob also include predicted frequency, strand bias score, depth
                        # predict frequency if site were to be constant? And see if it's less than tolerance?
                        # need to replace the TNC, requires encoding, mm mm love this
                        existing_tnc = site_info['tnc']
                        # check this, might need double index 
                        theoretical_tnc = existing_tnc[0] + base + existing_tnc[0]
                        theoretical_site_info_trans = pd.DataFrame([transformed_data.iloc[reference_position]])
                        theoretical_site_info_trans['tnc'] = label_encoders['tnc'].transform([theoretical_tnc])
                        theoretical_site_info_trans['ref_base'] = label_encoders['ref_base'].transform([base])
                        pred_f = dict(zip('ATGC',trained_model.predict(theoretical_site_info_trans)[0]))
                        if pred_f[base] - base_t > tolerance:
                            var_sites.append((reference_position,r,base,base_t,base_p,pred_f,SB,depth,'mixed'))
                            # print(f'Mixed site called: position {real_pos}, {r} to {base}; predicted (if constant) and true frequencies: {pred_f[base]}, {base_t}')
                        else:
                            var_sites.append((reference_position,r,base,base_t,base_p,pred_f,SB,depth,'constant'))
    return var_sites

# output
def write_initial_vcf(reference_name,output_vcf,variant_list):
    vh = pysam.VariantHeader()
    vh.add_meta(key='fileformat',value='VCFv4.2')
    vh.add_meta(key='fileDate',value=f'{datetime.date.today()}')
    vh.add_meta(key='source',value='rf_regressor_variant_calling')
    vh.add_meta(key='cmd',value='test_cmd')
    vh.add_meta(key='contig',items=[('ID',reference_name)])
    vh.add_meta('INFO',items=[('ID','DP'),('Number',1),('Type','Integer'),('Description','Total read depth at site')])
    vh.add_meta('INFO',items=[('ID','SB'),('Number','.'),('Type','Float'),('Description','Measure of strand bias for alt base(s)')])
    vh.add_meta('INFO',items=[('ID','AF'),('Number','.'),('Type','Float'),('Description','Frequency of alt allele(s)')])
    vh.add_meta('INFO',items=[('ID','PF'),('Number','.'),('Type','Float'),('Description','Predicted frequency of alt allele(s) if error')])
    vh.add_meta('INFO',items=[('ID','PFC'),('Number','.'),('Type','Float'),('Description','Predicted frequency of alt allele(s) if constant site')])
    vh.add_meta('INFO',items=[('ID','CON'),('Number','.'),('Type','String'),('Description','Variant classed as constant or mixed at this site')])
    with pysam.VariantFile(output_vcf,'w',header=vh) as vcf_out:
        for variant_tuple in variant_list:
            # assumes zero idx input and adds one
            pos,ref,alt,true_freq,pred_freq,pred_freq_constant_dict,sb,dp,class_ = variant_tuple
            pred_freq_constant = pred_freq_constant_dict[alt]
            allele_pos = int(pos)
            r = vcf_out.new_record(contig=reference_name,start=allele_pos,stop=allele_pos+1,alleles=(ref,alt),filter='PASS')
            r.info['DP'] = int(dp)
            r.info['SB'] = sb
            r.info['AF'] = true_freq
            r.info['PF'] = pred_freq
            r.info['PFC'] = pred_freq_constant
            r.info['CON'] = class_

            vcf_out.write(r)