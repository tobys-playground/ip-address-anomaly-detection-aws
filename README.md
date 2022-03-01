# IP Address Anomaly Detection (AWS SageMaker + Step Functions + CodePipeline)

## Background

It is common for users to hide their real IP addresses using a proxy like Tor, but is it possible to at least tell if an IP address belongs to a geographical location? I conducted an experiment using SageMaker's own IP Insights to see if it could identify IP addresses that do not belong to the regions they claim to be from.

The dataset was taken from GeoLite2 (http://dev.maxmind.com/geoip/geoip2/geolite2). I cleaned it to remove submasks and keep only 50 records each from the United States, the United Kingdom, France, Germany, and Canada as these countries had the most records. I also retrieved 5 records from Singapore to serve as outliers/anomalies.

The training data looks as below:

![image](https://user-images.githubusercontent.com/81354022/156147192-762b6a47-05b7-42b4-94a1-93540e5efc5b.png)

Each of the IP addresses from Singapore was then tagged to one of the 5 Western countries, and will be the test data for the model.

![image](https://user-images.githubusercontent.com/81354022/156128562-b3891295-ca73-43a9-9f14-417bc8c06990.png)

## MLOps

As a bonus, this repo contains a MLOps **CodePipeline** that will create a **Step Functions State Machine** when there is a change to the code, and fine-tune and deploy the **IP Insights model** with SageMaker.

1) A commit made to the **GitHub/CodeCommit** repository will trigger the **CodePipeline** and start the **CodeBuild** job
2) **CodeBuild** will create a **Step Functions State Machine** by running **step_function.py**
3) The **State Machine** will then be executed
4) The **IP Insights model** will be fine-tuned and deployed as an endpoint in **SageMaker**. If this is successful, the State Machine should look as below:

![image](https://user-images.githubusercontent.com/81354022/156137466-1848c710-06f6-46bb-910a-e8321be73f5f.png)

5) The model, endpoint config, and endpoint can be found in SageMaker, and the endpoint (Must be **InService**) can now be invoked:

![image](https://user-images.githubusercontent.com/81354022/156137803-fc676d7d-00c0-42e2-855c-d9b20255f8ec.png)

![image](https://user-images.githubusercontent.com/81354022/156137857-8bd57736-8ea8-447e-99d5-3e96608e0ee5.png)

![image](https://user-images.githubusercontent.com/81354022/156137941-fd11a8af-6444-420f-a250-06c2b536b953.png)

6) Optionally, users can **provision a Lambda function to create/update a Lambda Function and an API Gateway via CloudFormation** so that users can invoke the SageMaker endpoint over the Internet (An example: https://github.com/tobys-playground/google-search-results-aws-mlops-pt-2).

## Results

The test data was sent to the SageMaker endpoint for inference.

![image](https://user-images.githubusercontent.com/81354022/156130007-1bfec8c9-2618-4dde-94f4-6ab6aa348d64.png)

According to https://github.com/aws/amazon-sagemaker-examples/issues/1533, a negative score indicates dissimilarity. As such, **IP Insights has correctly identified that the Singapore IP addresses do not belong to the 5 Western countries and are outliers/anomalies**.

For its Azure counterpart, look at https://github.com/tobys-playground/ip-address-anomaly-detection-azure
