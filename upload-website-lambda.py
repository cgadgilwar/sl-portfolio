import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:418230580652:SLReactS3Website')

    try:
        s3 = boto3.resource('s3')

        website_build_bucket = s3.Bucket('sl-react-website-build')
        website_bucket = s3.Bucket('sl-react-website')

        website_zip = StringIO.StringIO()
        website_build_bucket.download_fileobj('slReactBuild.zip', website_zip)

        with zipfile.ZipFile(website_zip) as buildZip:
            for name in buildZip.namelist():
                print name
                obj = buildZip.open(name)
                website_bucket.upload_fileobj(obj, name,
                    ExtraArgs={'ContentType': mimetypes.guess_type(name)[0]})
                website_bucket.Object(name).Acl().put(ACL='public-read')

        topic.publish(Subject='Build Run Success', Message="Build deployed successfully")
    except:
        topic.publish(Subject='Build Run Failed', Message="Build deployed failed")

    return 'Done from Lambda!'
