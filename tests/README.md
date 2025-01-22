# Automated Testing

Automated testing is accomplished using AWS CodeBuild and Postman

```
export tf_venue=sit

```

**Running codebuild pipeline**

Always upload the most recent source (build spec plus postman test collection) to the S3 bucket:

```
aws s3 cp buildspec.yml  s3://podaac-services-${tf_venue}-deploy/internal/fts/buildspec.yml --profile ngap-service-${tf_venue}
aws s3 cp FTS.postman_collection.json s3://podaac-services-${tf_venue}-deploy/internal/fts/FTS.postman_collection.json --profile ngap-service-${tf_venue}
```

**Then run the build.**

Note: base_url must be updated with the api gateway url of the FTS internal api gateway.

```
aws codebuild start-build --project-name FTS --profile ngap-service-${tf_venue} --environment-variables-override name=base_url,value=https://hl41iaa049.execute-api.us-west-2.amazonaws.com,type=PLAINTEXT
```
