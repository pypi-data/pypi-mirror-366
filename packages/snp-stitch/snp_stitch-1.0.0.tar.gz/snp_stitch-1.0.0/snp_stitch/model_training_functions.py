import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
from concurrent.futures import ProcessPoolExecutor
import joblib
import warnings
import pysam
from collections import defaultdict
import pandas as pd
import numpy as np
from math import log
from pathlib import Path
import datetime
import itertools


# prob return them with the model as a full output dict
def training_main(path_to_datasets,model_dir,model_name,cores,estimator_range,depth_range,min_sample_range,min_leaf_range,min_impurity_range,folds):
    # parse the dataset to a df
    training_df = parse_datasets(path_to_datasets,cores)
    # train the model on that df
    model,encoder_dict = train_model(training_df,cores,estimator_range,depth_range,min_sample_range,min_leaf_range,min_impurity_range,folds)
    # write out the model to the specified path
    write_out_model_info(model,encoder_dict,model_dir,model_name)

def parse_datasets(path_to_datasets,cores):
    # for each subdir in datasets dir, get the reference file, get the mapped reads
    # expected dir structure looks like:
    # training_data/
    # ├── dataset1/
    # │     ├──reference1.fa
    # │     ├──excluded_sites1.bed (optional)
    # │     └──mapped_reads1/
    # │       ├── reads1.bam
    # │       ├── reads1.bam.bai
    # │       ├── reads2.bam
    # │       └── reads2.bam.bai
    # └── dataset2/
    #       ├──reference2.fa
    #       ├──excluded_sites2.bed (optional)
    #       └──mapped_reads2/
    #         ├── reads1.bam
    #         ├── reads1.bam.bai
    #         ├── reads2.bam
    #         └── reads2.bam.bai
    excluded_sites = []
    dfs_to_concat = []
    for dataset in os.listdir(path_to_datasets):
        # check it is a directory: error if not
        dataset_path = os.path.join(path_to_datasets,dataset)
        if not os.path.isdir(dataset_path):
            print(f"Skipping file: {dataset} in training data because it's not a directory")
        # check if reference fasta is present , error if not
        files_in_dataset = [x for x in os.listdir(dataset_path)]
        fastas = [os.path.join(dataset_path,file) for file in files_in_dataset if file.endswith('.fa') or file.endswith('.fasta') or file.endswith('.fna')]
        if len(fastas) != 1:
            raise ValueError(f'There is either a missing reference fasta or more than one reference fasta for dataset directory: {dataset}')
        # do all the ref specific calculations
        ref_seq = ''.join(open(fastas[0]).readlines()[1:]).replace('\n','')
        hp_dict = get_hp(ref_seq)
        tnc_dict = get_tnc(ref_seq)
        # sites to be excluded e.g. if good reason exists to suspect heterogeneity at that site
        beds = [os.path.join(dataset_path,file) for file in files_in_dataset if file.endswith('.bed')]
        if len(beds) > 0:
            for bedfile in beds:
                excluded_sites.extend(parse_excluded_bed(bedfile,dataset))
        read_dirs = [os.path.join(dataset_path,file) for file in files_in_dataset if os.path.isdir(dataset_path+'/'+file)]
        if len(read_dirs) == 0:
            raise ValueError(f'There is no read directory for dataset directory: {dataset}')
        elif len(read_dirs) > 1:
            warnings.warn(f'More than one read directory for dataset directory: {dataset}, all will be concatenated together')
        # check if all read_dirs are empty, error if is
        reads_present = False
        for read_dir in read_dirs:
            if len(os.listdir(read_dir)) > 0:
                reads_present = True
            read_paths = [os.path.join(read_dir,read_file) for read_file in os.listdir(read_dir) if read_file.endswith('.bam')]
            with ProcessPoolExecutor(max_workers=cores) as executor:
                data_list = list(executor.map(get_data_for_train,read_paths,itertools.repeat(tnc_dict),itertools.repeat(hp_dict),itertools.repeat(dataset)))
            dfs_to_concat.extend([pd.DataFrame.from_dict(data,orient='index') for data in data_list])
        if not reads_present:
            raise ValueError(f'No directories that contain read data for dataset {dataset}')
    # concatenate dfs
    df = pd.concat(dfs_to_concat)
    print('Data parsing complete')
    if len(excluded_sites) > 0:
        print(f'Dropping {len(excluded_sites)} sites from bed files')
        try:
            df.drop(excluded_sites)
        except KeyError:
            print(df.index)
            print(excluded_sites)
            raise
    return df


def parse_excluded_bed(bed_path,dataset_name):
    excluded = []
    with open(bed_path) as file:
        for line in file:
            line = line.strip('\n').split()
            site = line[1]
            excluded.append(f'{dataset_name}_{site}')
    return excluded


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
    # returns a dict of window_center:hp_percent
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
        window_vals[focal] = running_total/len(chunk)
        
    return window_vals

def get_data_for_train(bam_path,tnc_pos_dict,hp_pos_dict,dataset,max_depth=40000):
    print(f'Currently parsing read file: {bam_path} from dataset: {dataset}')
    base_dict = defaultdict(dict)
    bamfile = pysam.AlignmentFile(bam_path,'rb')    
    for pileupcolumn in bamfile.pileup(max_depth=max_depth):
        ref_pos = pileupcolumn.reference_pos
        pos_key = f'{dataset}_{ref_pos}'
        base_list_at_pos = [x.alignment.query_sequence[x.query_position] for x in pileupcolumn.pileups if not x.is_del and not x.is_refskip]
        try:
            base_dict[pos_key]['freqs_A'] = base_list_at_pos.count('A')/len(base_list_at_pos)
            base_dict[pos_key]['freqs_T'] = base_list_at_pos.count('T')/len(base_list_at_pos)
            base_dict[pos_key]['freqs_C'] = base_list_at_pos.count('C')/len(base_list_at_pos)
            base_dict[pos_key]['freqs_G'] = base_list_at_pos.count('G')/len(base_list_at_pos)

            try:
                tnc = tnc_pos_dict[ref_pos]
                base_dict[pos_key]['tnc'] = tnc
                # this might be completely unnecessary, can't remember if I padded ends
                if len(tnc) == 3:
                    base_dict[pos_key]['ref_base'] = tnc[1]
                elif ref_pos == 0:
                    base_dict[pos_key]['ref_base'] = tnc[0]
                else:
                    base_dict[pos_key]['ref_base'] = tnc[1]

            except KeyError:
                warnings.warn(f'A position with no tnc assigned? Position {pos_key}')
                base_dict[pos_key]['tnc'] = None
            try:
                base_dict[pos_key]['hp_content'] = hp_pos_dict[ref_pos]
            except KeyError:
                warnings.warn(f'A position with no hp content assigned? Position {pos_key}')
                base_dict[pos_key]['hp_content'] = None
            base_dict[pos_key]['source'] = dataset
            base_dict[pos_key]['depth'] = pileupcolumn.nsegments

        except ZeroDivisionError:
            # I think a low coverage warning and don't include the position
            warnings.warn(f'No reads mapping at position {ref_pos}, or possibly no bases meeting min quality')
        
            
    return base_dict


def write_out_model_info(model,encoders,model_dir_path,model_name):
    # make a new subdir in the model path called the model name?
    try:
        model_sub_dir = model_name
        Path(os.path.join(model_dir_path,model_sub_dir)).mkdir()
    except FileExistsError:
        print(f'Model name already exists in this location, appending date to distinguish')
        model_sub_dir = f'{model_name}_{datetime.date.today()}'
        Path(os.path.join(model_dir_path,model_sub_dir)).mkdir()
    print(f'Writing model and encoders to directory: {os.path.join(model_dir_path,model_sub_dir)}')
    joblib.dump(model,os.path.join(model_dir_path,model_sub_dir,'regressor.pkl.gz'),compress=9)
    for feature in encoders:
        joblib.dump(encoders[feature],os.path.join(model_dir_path,model_sub_dir,f'{feature}_encoder.pkl'))
    print('Complete')
        


def train_model(df,cores,estimator_range,depth_range,min_sample_range,min_leaf_range,min_impurity_range,folds):
    df2 = df.copy(deep=True)
    df2.dropna(inplace=True)

    cols = [x for x in df2.columns if 'freqs' not in x and 'quals' not in x and x != 'quals' and x != 'index' and x != 'source']
    x = df2[cols]
    y = df2[['freqs_A','freqs_T','freqs_G','freqs_C']]

    label_encoder = LabelEncoder()
    encoder_dict = {}

    cat_cols = x.select_dtypes(include=['object']).columns
    cat_vals = pd.DataFrame(index=x.index)
    for col in cat_cols:
        cat_vals[col] = label_encoder.fit_transform(x[col])
        encoder_dict[col] = label_encoder
        label_encoder = LabelEncoder()
    num_cols = x.select_dtypes(exclude=['object']).columns
    num_vals = x.select_dtypes(exclude=['object'])

    x = pd.concat([pd.DataFrame(num_vals,index=cat_vals.index), cat_vals], axis=1).values
    x = pd.DataFrame(x,columns=[*num_cols,*cat_cols])
 
    # Number of trees in random forest
    n_estimators = [int(x) for x in np.linspace(start = estimator_range[0], stop = estimator_range[1], num = 10)]
    # Number of features to consider at every split
    max_features = ['log2','sqrt',None,0.5]
    # Maximum number of levels in tree
    max_depth = [int(x) for x in np.linspace(depth_range[0], depth_range[1], num = 11)]
    max_depth.append(None)
    # Minimum number of samples required to split a node
    min_samples_split = [int(x) for x in np.linspace(start = min_sample_range[0], stop = min_sample_range[1], num = 4)]
    # Minimum number of samples required at each leaf node
    min_samples_leaf = [int(x) for x in np.linspace(start = min_sample_range[0], stop = min_sample_range[1], num = 4)]
    # Min decrease in impurity to create a split
    min_impurity_decrease = [int(x) for x in np.linspace(start = min_impurity_range[0], stop = min_impurity_range[1], num = 4)]

    param_grid = {'n_estimators': n_estimators,
                'max_features': max_features,
                'max_depth': max_depth,
                'min_samples_split': min_samples_split,
                'min_samples_leaf': min_samples_leaf,
                'min_impurity_decrease':min_impurity_decrease}
    regressor = RandomForestRegressor(oob_score=True)
    random_search = RandomizedSearchCV(regressor,param_grid,cv=folds,n_iter=100,scoring='neg_mean_squared_error',n_jobs=cores,verbose=True)
    rand_res = random_search.fit(x,y)
    regressor = rand_res.best_estimator_
    print(f'Cross validation has selected these parameters for the best estimator with a score of {rand_res.best_score_} (negative MSE)')
    print(regressor)
    regressor.fit(x,y)

    oob_score = regressor.oob_score_
    print(f'Out-of-Bag Score: {oob_score}')
    predictions = regressor.predict(x)
    mse = mean_squared_error(y, predictions)
    print(f'Mean Squared Error on training set: {mse}, RMSE: {mse**0.5}')
    r2 = r2_score(y, predictions)
    print(f'R-squared: {r2}')
    print()
    # feature importances
    print('Feature        Relative importance')
    for feature, imp in zip(list(x.columns),regressor.feature_importances_):
        print(f'{feature:15}{imp}')
    print()
    return regressor,encoder_dict



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
 