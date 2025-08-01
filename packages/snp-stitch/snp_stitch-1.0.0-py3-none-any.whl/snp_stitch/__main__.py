import argparse
import sys
import datetime
from pathlib import Path
from .variant_calling_functions import *
from .model_training_functions import *

# main running of everything
def main(sysargs=sys.argv[1:]):

    parser = argparse.ArgumentParser(add_help=True)
    subparser = parser.add_subparsers()
    call_parser = subparser.add_parser('call',help='call variants using pre-trained model')
    train_parser = subparser.add_parser('train',help='train a new model on known sequences')

    call_parser.add_argument('-b',"--bam",help="Path to mapped reads in bam format", dest="bam_path")
    call_parser.add_argument('-r','--reference_fasta',help='Reference fasta to map reads and call variants against',dest='ref')
    call_parser.add_argument('-o','--out_dir',help='Path to directory for output. Default: snp_stitch_output_DATE',default=f'snp_stitch_output_{datetime.date.today()}',dest='output_dir')
    call_parser.add_argument('-e','--tolerance',help='Tolerance for error when calling variants. Default:0.02',default=0.02,dest='tol',type=float)
    call_parser.add_argument('-m','--models',help='Path to dir with model and encoder files',default=os.path.join(Path(__file__).parent,'models'),dest='models_path')
    call_parser.add_argument('-p','--cores',help='Number of cores to use. Default:1',default=1,dest='cores')

    train_parser.add_argument('-d',"--data_dir",help="Path to datasets to be used in training; must contain reference sequence and mapped reads", dest="data_dir")
    train_parser.add_argument('-mo','--models_output',help='Path to dir to store model and encoder files. Default:user_models',default='user_models',dest='user_models_path')
    train_parser.add_argument('-mn','--model_name',help='Name of subdirectory in models output dir storing this model. Default:new_model',default='new_model',dest='user_model_name')
    train_parser.add_argument('-p','--cores',help='Number of cores to use. Default:1',default=1,dest='cores',type=int)
    train_parser.add_argument('-rt','--range_trees',help='Range of estimator counts to consider in the random forest during optimisation. Default:50 175',default=(50,175),dest='estimator_range',nargs=2,type=int)
    train_parser.add_argument('-rd','--tree_depth',help='Range of depths to consider in the random forest during optimisation. Default 50 175',default=(50,175),dest='depth_range',nargs=2,type=int)
    train_parser.add_argument('-ms','--min_split',help='Range of values for minimum sample split to consider in the random forest during optimisation. Default: 5 10',default=(5,10),dest='min_split_range',nargs=2,type=int)
    train_parser.add_argument('-ml','--min_leaf',help='Range of values for minimum leaf samples to consider in the random forest during optimisation. Default: 3 5',default=(3,5),dest='min_leaf_range',nargs=2,type=int)
    train_parser.add_argument('-mi','--min_impurity',help='Range of values for the minimum impurity decrease to consider in the random forest during optimisation - must be in [0,1]. Default:0 0.5',default=(0,0.5),dest='min_imp_range',nargs=2,type=float)
    train_parser.add_argument('-cv','--cv_folds',help='The number of folds to use for k-folds cross validation during optimisation. Default:5',default=5,dest='folds',type=int)
    # if no arguments provided
    if len(sysargs)<1: 
        parser.print_help()
        sys.exit(0)
    elif len(sysargs)==1:
        match sysargs[0]:
            case 'call':
                call_parser.print_help()
                sys.exit(0)
            case 'train':
                train_parser.print_help()
                sys.exit(0)
            case _:
                print(f'Not a valid subcommand: {sysargs[0]}')
                parser.print_help()
                sys.exit(1)
    else:
        args = parser.parse_args(sysargs)
        print('''
        ######################################################
        #                                                    #
        #  ___  _ _  ___         ___  ___  _  ___  ___  _ _  #
        # / __>| \ || . \  ___  / __>|_ _|| ||_ _||  _>| | | #
        # \__ \|   ||  _/ |___| \__ \ | | | | | | | <__|   | #
        # <___/|_\_||_|         <___/ |_| |_| |_| `___/|_|_| #
        #                                                    #
        ######################################################''')

    match sysargs[0]:
        case 'call':
            if not args.ref:
                print("Reference fasta must be provided!")
                sys.exit(1)
            elif not (args.bam_path or args.unmapped_reads):
                print("Mapped reads must be provided!")
                sys.exit(1)
            Path(args.output_dir).mkdir(parents=True, exist_ok=True)
            print(f'Calling variants against reference {args.ref} for file {args.bam_path}...')
            ref_name,tnc_dict, hp_dict = prep_ref_seq_features(ref_fasta=args.ref)
            vars = get_variant_sites(test_bam=args.bam_path,tnc_dict=tnc_dict,hp_dict=hp_dict,tolerance=args.tol,model_and_encoder_dir=args.models_path)
            print(f'Writing vcf to output directory {args.output_dir}')
            write_initial_vcf(ref_name,f'{args.output_dir}/output.vcf',vars)
        case 'train':
            Path(args.user_models_path).mkdir(parents=True, exist_ok=True)
            print(f'Training a new model using data in {args.data_dir}')
            training_main(args.data_dir,args.user_models_path,args.user_model_name,args.cores,args.estimator_range,args.depth_range,args.min_split_range,args.min_leaf_range,args.min_imp_range,args.folds)

if __name__ == '__main__':
    main()
