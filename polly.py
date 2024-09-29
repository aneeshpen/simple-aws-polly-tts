import os
import boto3
import uuid
import tempfile  # Import the tempfile module to handle temporary file storage

# Retrieve credentials and region from environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

# Initialize Polly and S3 clients
polly_client = boto3.client(
    'polly',
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)
s3_client = boto3.client(
    's3',
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# Function to generate speech and upload it to S3
def text_to_speech(input_text, voice_id='Joanna'):
    """
    Converts text to speech using Amazon Polly and uploads the file to an S3 bucket.
    :param input_text: The text to convert to speech.
    :param voice_id: The voice to be used for the speech.
    :return: Public URL of the uploaded speech file in S3.
    """
    # Call Polly to synthesize speech
    response = polly_client.synthesize_speech(
        Text=input_text,
        OutputFormat='mp3',
        VoiceId=voice_id
    )
    
    # Generate unique filename
    audio_file = f"{uuid.uuid4()}.mp3"
    
    # Use tempfile to generate a temporary file path that works cross-platform
    with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
        temp_audio_path = temp_audio_file.name
        temp_audio_file.write(response['AudioStream'].read())
    
    # Upload the file to S3
    bucket_name = ''  # Replace with your S3 bucket name
    s3_client.upload_file(temp_audio_path, bucket_name, audio_file)
    
    # Create and return the S3 public link
    download_link = f"https://{bucket_name}.s3.amazonaws.com/{audio_file}"
    
    # Clean up the temporary file
    os.remove(temp_audio_path)
    
    return download_link

# Function to interact with the user and generate speech
def main():
    # Ask the user for the text to convert to speech
    input_text = input("Enter the text you want to convert to speech: ")
    
    # Provide a list of voices for the user to choose from
    available_voices = {
        '1': 'Joanna (English US - Female)',
        '2': 'Matthew (English US - Male)',
        '3': 'Miguel (Spanish - Male)',
        '4': 'Lucia (Spanish - Female)'
    }

    print("Choose a voice from the list:")
    for key, voice in available_voices.items():
        print(f"{key}: {voice}")

    voice_choice = input("Enter the number corresponding to your choice of voice: ")

    # Map user choice to Polly voice IDs
    voice_id_map = {
        '1': 'Joanna',
        '2': 'Matthew',
        '3': 'Miguel',
        '4': 'Lucia'
    }

    # Default to 'Joanna' if input is invalid
    voice_id = voice_id_map.get(voice_choice, 'Joanna')

    # Generate the speech file and get the S3 link
    s3_link = text_to_speech(input_text, voice_id)
    
    print(f"Your speech file is ready! Download it from: {s3_link}")

if __name__ == '__main__':
    main()
