# Book Summarizer

Create an abstractive summary of books

Project as part of Insight AI

## Project contents:
- **Book_Summarizer** : All source code
- **tests** : Source code for testing
- **configs** : Files for modification of all preset variables
- **data** : Sample data 

## Setup
Clone repository and update python path
```
repo_name=Book_Summarizer # URL of your new repository
username=ruthschulz # Username for your personal github account
git clone https://github.com/$username/$repo_name
cd $repo_name
echo "export $repo_name=${PWD}" >> ~/.bash_profile
echo "export PYTHONPATH=$repo_name/src:${PYTHONPATH}" >> ~/.bash_profile
source ~/.bash_profile

## Requisites

- All packages and software needed to build the environment

#### Installation
To install the packages above, pleae run:
```shell
pip install -r requirements
```

## Run

cd Book_Summarizer
python book_summarizer.py

The program will then ask you to enter the title of the book to summarize, choose from a list which book from Project Gutenberg to download, then print a summary of the book to the terminal.

## Test
- Include instructions for how to run all tests after the software is installed
```
# Example

# Step 1
# Step 2
```

## Run Inference
- Include instructions on how to run inference
- i.e. image classification on a single image for a CNN deep learning project
```
# Example

# Step 1
# Step 2
```

## Build Model
- Include instructions of how to build the model
- This can be done either locally or on the cloud
```
# Example

# Step 1
# Step 2
```

## Serve Model
- Include instructions of how to set up a REST or RPC endpoint
- This is for running remote inference via a custom model
```
# Example

# Step 1
# Step 2
```

## Analysis
- Include some form of EDA (exploratory data analysis)
- And/or include benchmarking of the model and results
```
# Example

# Step 1
# Step 2
```
