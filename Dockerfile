FROM python:3.8
ADD GetNFTFromCollection.py .
RUN pip install pika moralis    
CMD ["python","./GetNFTFromCollection.py"]

