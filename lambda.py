import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event['s3_key']                              
    bucket = event['s3_bucket']
    
    
    s3.download_file(bucket, key, "/tmp/image.png")
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }
''' *******************************************************************************************'''


import json
import sagemaker
import base64
from sagemaker.predictor import Predictor
from sagemaker.serializers import IdentitySerializer

ENDPOINT = "image-classification-2024-08-04-14-53-31-369"

def lambda_handler(event, context):
    print(event)
    try:
        # Decode the image data
        image = base64.b64decode(event['body']['image_data'])
        
        # Instantiate a Predictor
        predictor = Predictor(ENDPOINT)
        print(predictor)
        # For this model the IdentitySerializer needs to be "image/png"
        predictor.serializer = IdentitySerializer("image/png")
        
        # Make a prediction:
        inferences = predictor.predict(image)
        
        # We return the data back to the Step Function    
        event['body']["inferences"] = inferences.decode('utf-8')
        return {
            'statusCode': 200,
            'body': json.dumps(event['body'])
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }


''' *******************************************************************************************'''

import json


THRESHOLD = 0.93


def lambda_handler(event, context):
    
    # Grab the inferences from the event
    body = json.loads(event['body'])
        
    # Grab the inferences from the parsed body
    inferences = json.loads(body['inferences'])
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(list(inferences)) > THRESHOLD
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error 
    print(meets_threshold)
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
