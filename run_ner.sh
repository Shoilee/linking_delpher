#!/bin/bash

# Script to activate conda env and run NER function with arguments

# Default values (override with command line args)
CONDA_ENV="${1:-dutch_NER}"              # conda environment name
MODEL_NAME="${2:-dslim/bert-base-NER}"  # NER model name
TEXT="${3:-}"                      # Input text for NER
LABEL_LIST="${4:-'O', 'B-PER', 'I-PER', 'B-ORG', 'I-ORG', 'B-LOC', 'I-LOC', 'B-MISC', 'I-MISC'}"  # Labels

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Starting NER Pipeline...${NC}"
echo -e "${YELLOW}Conda env:${NC} $CONDA_ENV"
echo -e "${YELLOW}Model:${NC} $MODEL_NAME"
echo -e "${YELLOW}Text length:${NC} ${#TEXT} chars"
echo -e "${YELLOW}Labels:${NC} $LABEL_LIST"
echo

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo -e "${RED}Error: conda not found${NC}"
    exit 1
fi

# Activate conda environment
echo -e "${YELLOW}Activating: $CONDA_ENV${NC}"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to activate '$CONDA_ENV'${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment activated${NC}"
echo

# Check if required Python module exists
python -c "from ner.ner_wrapper import ner" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: 'ner.ner_wrapper' module not found${NC}"
    echo "Make sure you're in the right directory with ner/ner_wrapper.py"
    exit 1
fi

# Build Python one-liner to call ner() function
PYTHON_CMD="
from ner.ner_wrapper import ner
model_name = '$MODEL_NAME'
label_list = [$LABEL_LIST]
text = '''$TEXT'''
ner(model_name, label_list, text)

"

echo -e "${YELLOW}Running NER...${NC}"
echo "----------------------------------------"

# Execute the NER function
python3 -c "$PYTHON_CMD"

EXIT_CODE=$?

echo "----------------------------------------"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ NER completed successfully${NC}"
else
    echo -e "${RED}✗ NER failed (code $EXIT_CODE)${NC}"
fi

conda deactivate
echo -e "${GREEN}✓ Environment deactivated${NC}"

exit $EXIT_CODE
