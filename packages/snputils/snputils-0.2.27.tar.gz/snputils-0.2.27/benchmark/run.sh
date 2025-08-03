#!/bin/bash

# Parse command line arguments
DATA_DIR="data"  # default value
FORMATS=()  # array to store selected formats
CHROMS=()  # array to store selected chromosomes

function print_usage() {
    echo "Usage: $0 [--data-dir <dir>] [--formats <format1,format2,...>] [--chroms <chrom1,chrom2,...>]"
    echo "Available formats: vcf, bed, pgen"
    echo "Available chromosomes: chr1, chr22, whole_genome"
    echo "Example: $0 --formats vcf,bed --chroms chr1,whole_genome"
    echo "If no formats are specified, all formats will be run"
    echo "If no chromosomes are specified, chr1, chr22, and whole_genome will be run"
}

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --data-dir) DATA_DIR="$2"; shift ;;
        --formats) 
            IFS=',' read -ra FORMATS <<< "$2"
            # Validate formats
            for format in "${FORMATS[@]}"; do
                if [[ ! "$format" =~ ^(vcf|bed|pgen)$ ]]; then
                    echo "Invalid format: $format"
                    print_usage
                    exit 1
                fi
            done
            shift ;;
        --chroms)
            IFS=',' read -ra CHROMS <<< "$2"
            # Validate chromosomes
            for chrom in "${CHROMS[@]}"; do
                if [[ ! "$chrom" =~ ^(chr1|chr22|whole_genome)$ ]]; then
                    echo "Invalid chromosome: $chrom"
                    print_usage
                    exit 1
                fi
            done
            shift ;;
        --help|-h)
            print_usage
            exit 0 ;;
        *) echo "Unknown parameter: $1"; print_usage; exit 1 ;;
    esac
    shift
done

# If no formats specified, use all
if [ ${#FORMATS[@]} -eq 0 ]; then
    FORMATS=("vcf" "bed" "pgen")
fi

# If no chromosomes specified, use all available options
if [ ${#CHROMS[@]} -eq 0 ]; then
    CHROMS=("chr1" "chr22" "whole_genome")
fi

echo "Will run benchmark for formats: ${FORMATS[*]}"
echo "Will run benchmark for chromosomes: ${CHROMS[*]}"

# Create directory structure
mkdir -p ${DATA_DIR}/vcf ${DATA_DIR}/bed ${DATA_DIR}/pgen benchmark/sbatch benchmark/results

# Determine zip file based on OS
case "$(uname -s)" in
    Darwin*)
        zip_file="plink2_mac_arm64_20241114.zip"
        ;;
    Linux*)
        zip_file="plink2_linux_x86_64_20241114.zip"
        ;;
    *)
        echo "Error: You will need to manually download and setup plink2 for your OS"
        exit 1
        ;;
esac

# Download and setup plink2 if not already present
if [ ! -f ${DATA_DIR}/plink2 ]; then
    wget -P ${DATA_DIR} https://s3.amazonaws.com/plink2-assets/alpha6/${zip_file}
    unzip ${DATA_DIR}/${zip_file} -d ${DATA_DIR}
    chmod +x ${DATA_DIR}/plink2
    rm ${DATA_DIR}/${zip_file}
fi

# Base URL for 1000 genomes data
BASE_URL="https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000_genomes_project/release/20181203_biallelic_SNV"

# Determine which chromosomes need to be downloaded
NEED_CHR1=false
NEED_CHR22=false
NEED_ALL=false

for chrom in "${CHROMS[@]}"; do
    case $chrom in
        "chr1") NEED_CHR1=true ;;
        "chr22") NEED_CHR22=true ;;
        "whole_genome") NEED_ALL=true ;;
    esac
done

# Download VCF files and convert to PGEN if they don't exist
if [[ " ${FORMATS[@]} " =~ " pgen " ]] || [[ " ${FORMATS[@]} " =~ " bed " ]] || [[ " ${FORMATS[@]} " =~ " vcf " ]]; then
    for i in {1..22}; do
        # Skip chromosomes we don't need
        if ! $NEED_ALL; then
            if [ $i -eq 1 ] && ! $NEED_CHR1; then
                continue
            fi
            if [ $i -eq 22 ] && ! $NEED_CHR22; then
                continue
            fi
            if [ $i -ne 1 ] && [ $i -ne 22 ]; then
                continue
            fi
        fi

        vcf_file="${DATA_DIR}/vcf/ALL.chr${i}.shapeit2_integrated_v1a.GRCh38.20181129.phased.vcf.gz"
        pgen_file="${DATA_DIR}/pgen/ALL.chr${i}.shapeit2_integrated_v1a.GRCh38.20181129.phased.pgen"
        
        if [ ! -f "$vcf_file" ]; then
            wget -P ${DATA_DIR}/vcf "${BASE_URL}/ALL.chr${i}.shapeit2_integrated_v1a.GRCh38.20181129.phased.vcf.gz"
        fi
        
        if [[ " ${FORMATS[@]} " =~ " pgen " ]] && [ ! -f "$pgen_file" ]; then
            ${DATA_DIR}/plink2 --vcf "$vcf_file" --make-pgen --out "${DATA_DIR}/pgen/ALL.chr${i}.shapeit2_integrated_v1a.GRCh38.20181129.phased"
        fi
    done
fi

# Create a merge list file for plink2 with PGEN files if whole_genome is needed
if [[ " ${CHROMS[@]} " =~ "whole_genome" ]]; then
    if [ ! -f ${DATA_DIR}/pgen/merge_list.txt ]; then
        > ${DATA_DIR}/pgen/merge_list.txt  # Clear/create file
        for i in {2..22}; do
            echo "${DATA_DIR}/pgen/ALL.chr${i}.shapeit2_integrated_v1a.GRCh38.20181129.phased" >> ${DATA_DIR}/pgen/merge_list.txt
        done
    fi

    # Merge PGEN files using plink2 if not already done
    if [ ! -f ${DATA_DIR}/pgen/ALL.GRCh38.20181129.phased.pgen ]; then
        ${DATA_DIR}/plink2 \
            --pfile "${DATA_DIR}/pgen/ALL.chr1.shapeit2_integrated_v1a.GRCh38.20181129.phased" \
            --pmerge-list ${DATA_DIR}/pgen/merge_list.txt \
            --make-pgen \
            --out "${DATA_DIR}/pgen/ALL.GRCh38.20181129.phased"
    fi
fi

# Convert whole genome PGEN to VCF if needed
if [[ " ${FORMATS[@]} " =~ " vcf " ]] && [[ " ${CHROMS[@]} " =~ "whole_genome" ]]; then
    if [ ! -f ${DATA_DIR}/vcf/ALL.GRCh38.20181129.phased.vcf.gz ]; then
        ${DATA_DIR}/plink2 \
            --pfile "${DATA_DIR}/pgen/ALL.GRCh38.20181129.phased" \
            --export vcf bgz \
            --out "${DATA_DIR}/vcf/ALL.GRCh38.20181129.phased"
    fi
fi

# Convert to BED format for required files if needed
if [[ " ${FORMATS[@]} " =~ " bed " ]]; then
    for chrom in "${CHROMS[@]}"; do
        if [ "$chrom" = "whole_genome" ]; then
            base_name="ALL.GRCh38.20181129.phased"
        else
            num="${chrom#chr}"
            base_name="ALL.chr${num}.shapeit2_integrated_v1a.GRCh38.20181129.phased"
        fi
        
        if [ ! -f "${DATA_DIR}/bed/${base_name}.bed" ]; then
            ${DATA_DIR}/plink2 --pfile "${DATA_DIR}/pgen/${base_name}" --make-bed --out "${DATA_DIR}/bed/${base_name}"
        fi
    done
fi

# Create and submit job scripts for selected formats and chromosomes
for format in "${FORMATS[@]}"; do
    for chrom in "${CHROMS[@]}"; do
        if [ "$chrom" = "whole_genome" ]; then
            base_name="ALL.GRCh38.20181129.phased"
        else
            num="${chrom#chr}"
            base_name="ALL.chr${num}.shapeit2_integrated_v1a.GRCh38.20181129.phased"
        fi
        
        job_script="benchmark/sbatch/${format}_${chrom}.sh"
        echo "#!/bin/bash" > "$job_script"
        echo "pytest benchmark/read_${format}.py --path=${DATA_DIR}/${format}/${base_name} --benchmark-json=benchmark/results/${format}_${chrom}_4.json" >> "$job_script"
        chmod +x "$job_script"
        
        # Submit job
        sbatch \
            --mem=1024G \
            --cpus-per-task=32 \
            --time=24:00:00 \
            --partition=long \
            --output=benchmark/results/${format}_${chrom}_4.out \
            --error=benchmark/results/${format}_${chrom}_4.err \
            "$job_script"
    done
done

# Optional: Wait for all jobs to complete
echo "All jobs have been submitted for formats: ${FORMATS[*]}"
echo "All jobs have been submitted for chromosomes: ${CHROMS[*]}"
echo "Use 'squeue' to monitor their status."