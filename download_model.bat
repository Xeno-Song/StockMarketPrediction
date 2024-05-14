@echo off
echo.
echo #####################################################################
echo  Start to download FinBERT model from hunngin face.
echo  It may takes serveral minutes...
echo #####################################################################
echo.

git lfs install
git clone https://huggingface.co/ProsusAI/finbert finbert_model
