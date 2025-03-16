# **Data Lake Ingestion Pipeline using AWS Step Functions, EMR Serverless, and PySpark**

## **Project Overview**
This project automates the creation and execution of an AWS EMR Serverless application, which runs a PySpark job to ingest data from a PostgreSQL database (hosted on pgAdmin) into an S3 bucket (raw layer). The entire workflow is orchestrated using AWS Step Functions, ensuring seamless execution and resource management.

![architecture](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/architecture.jpg)


[Architecture Link](https://lucid.app/lucidchart/a9535ec7-ba9e-40c7-98c4-9836e920a7d9/edit?invitationId=inv_2dc9ef0f-af75-4e5f-ae7e-1dcf676f56fa)

## **Prerequisites**
- [s3](https://bitbucket.org/ivorsource/s3/src/main/)
- [IAM](https://bitbucket.org/ivorsource/iam_roles/src/IAM_Roles/)
- [secret Manger](https://bitbucket.org/ivorsource/secretsmanager/src/SecretsManager/)
- [Simple Queue Service (SQS)](https://bitbucket.org/ivorsource/sqs/src/SQS/)
- [Simple Notification Service (SNS)](https://bitbucket.org/ivorsource/sns/src/SNS/)
- [EMR cluster](https://bitbucket.org/ivorsource/emr/src/DE-1567/)
- [AWS Event Bridge](https://bitbucket.org/ivorsource/aws-eventbridge-scheduler-documentation/src/main/)

---

## **project Step-By-Step process**

1. **AWS Account:** Ensure you have an AWS account with the necessary permissions to create EMR Serverless applications, Step Functions, and S3 buckets.
2. **S3 Bucket:** Create an S3 bucket (`uexpertlyrecords`) with the following structure:
       - `logs/`: For storing EMR logs.
       - `jar/`: For storing the PostgreSQL JDBC driver (`postgresql-42.7.5.jar`).
       - `script/`: For storing the PySpark script (`Sparkscript.py`).
       - `raw-layer/`: For storing the processed data ingested from PostgreSQL.
   
![S3 Bucket](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/S3_bucket.jpg)

*Figure: S3 Bucket*  

3. **PostgreSQL Database:** Ensure the database is accessible from EMR Serverless and the credentials are correctly configured in the PySpark script.

## **Scripts and IAM Roles**
Before executing the EMR Serverless workflow, a PySpark script is used to extract, transform, and load (ETL) data from a PostgreSQL database to an Amazon S3 bucket. The script follows these key steps:

![IAM ROLES](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/IAM_user.jpg)

*Figure: IAM ROLE*

### **1. Secrets Management**
The script retrieves AWS credentials and PostgreSQL credentials from AWS Secrets Manager for secure access.

- **AWS credentials** include the access key, secret key, and region.
- **PostgreSQL credentials** include the host, username, password, database name, and port.


### **2. Spark Session Initialization**
A Spark session is created to process the data. The session is configured to interact with Amazon S3 and PostgreSQL.

- AWS S3 access is configured using retrieved credentials.
- The PostgreSQL JDBC driver is used to establish a connection to the database.

### **3. Data Extraction**
The script reads data from a PostgreSQL table using the JDBC driver.

- The source table is specified within the database.
- User credentials and driver settings are applied to fetch the data securely.

### **4. Data Transformation**
After fetching the data, the script performs transformations, including:

- Extracting month and year values from a date column.
- Cleaning and structuring data fields.
- Formatting certain fields for compatibility with downstream analytics.

### **5. Data Storage**
The transformed data is written to an Amazon S3 bucket in CSV format, partitioned by year and month for efficient querying and storage optimization.

- The bucket and folder structure follow a logical partitioning approach.
- The script ensures data integrity by writing files in overwrite mode.

### **6. Spark Job Completion**
Once the data is successfully written to S3, the Spark session is stopped to release resources.

---

## **Simple Queue Service**

### Amazon SQS Queue: `stepfunction_datapipeline`
- **Queue ARN**: `arn:aws:sqs:us-east-1:537124961883:stepfunction_datapipeline`
- **Encryption**: Amazon SQS key (SSE-SQS)
- **Queue URL**: [SQS URL](https://sqs.us-east-1.amazonaws.com/537124961883/stepfunction_datapipeline)
- **Dead-letter Queue**: Not configured (optional)

![SQS Queue](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/SQS.jpg)

*Figure: SQS Queue*


### SNS Subscriptions for the SQS Queue:
1. **`failurejob` Topic Subscription**:
       - **SNS Subscription ARN**: `arn:aws:sns:us-east-1:537124961883:failurejob:e42ea856-26d4-47ee-8cfb-4b973cc4f821`
       - **Subscription Type**: SQS

2. **`StepFunctionDataPipelineNotification` Topic Subscription**:
       - **SNS Subscription ARN**: `arn:aws:sns:us-east-1:537124961883:StepFunctionDataPipelineNotification:17fd3e1e-fda0-422e-9f11-b15ced3ed4e4`
       - **Subscription Type**: SQS


### Next Steps:
- Now that the subscriptions are in place, your SQS queue will receive notifications for both job success and failure.

---

## **Simple Notification Service** 
- AWS Simple Notification Service(SNS) is fully manged messaging service that enables message delivery from publisher to subscribers.
- it supports multiple messaging formats, that including SMS, Email, and AWS services such as SQS and Lambda.

- In our project, I have used SNS for sending messeges based on our task success or failure. After execution of Spark job we will be having a success or failure job 


## AWS SNS Setup for Notifications

### Prerequisites
- Ensure you have an AWS account and appropriate permissions to create SNS topics and subscriptions.
- Access to AWS Management Console or AWS CLI.

### Step 1: Create an SNS Topic

1. **Sign in to the AWS Console**:
   - Visit the [AWS SNS Console](https://console.aws.amazon.com/sns)

2. **Create a New Topic**:
       - Click **Create topic**.
       - Choose **Standard** or **FIFO** (depending on your needs).
       - Provide a **Topic name** (e.g., `StepFunctionDataPipelineNotification`).
       - (Optional) Set a **Display name** for SMS notifications.
       - Click **Create topic**.
   
### Step 2: Create Subscriptions

#### 2.1 Subscribe an Email Address

1. **In the SNS Console**, select your newly created topic, e.g., `arn:aws:sns:us-east-1:537124961883:StepFunctionDataPipelineNotification`.
2. Click **Create subscription**.
3. Choose **Protocol**: `Email`.
4. Enter the **Endpoint (Email Address)**: `chaithanya27.kasireddy@gmail.com`.
5. Click **Create subscription**.
6. **Confirm the subscription**:
       - Check your inbox for an email from AWS SNS.
       - Click the confirmation link in the email to activate the subscription.


![SQS Queue](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/SNS-subscription_jobsuccess.jpg)

*Figure: SNS Queue success*

### Subscription Details:
You now have two subscriptions for the topic:

- **SQS**: `arn:aws:sqs:us-east-1:537124961883:stepfunction_datapipeline`
- **Email**: `chaithanya27.kasireddy@gmail.com`

Both are confirmed, meaning you will receive notifications via email and SQS when messages are published to the topic.

## AWS SNS Topic for Job Failure Notifications

### Topic Details:
- **Topic Name**: `failurejob`
- **ARN**: `arn:aws:sns:us-east-1:537124961883:failurejob`
- **Type**: Standard
- **Topic Owner**: `537124961883`

![SNS Queue](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/Sns%20Failure.jpg)

*Figure: SnS Queue failure*


### Subscriptions:
- creating subscription job success and failure

![SNS Queue](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/sns_create_subscription_jobfailure.jpg) 

*Figure: SQS Queue subscription*

You have two confirmed subscriptions for this topic:

1. **Email Subscription**:
       - **Endpoint**: `chaithanya27.kasireddy@gmail.com`
       - **Protocol**: `Email`
       - **Status**: Confirmed

2. **SQS Subscription**:
       - **Endpoint**: `arn:aws:sqs:us-east-1:537124961883:stepfunction_datapipeline`
       - **Protocol**: `SQS`
       - **Status**: Confirmed

![SNS Queue](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/sns%20topic%20success.jpg)

*Figure: SNS Queue subscription*

## **Networking Configuration**
- **Subnet IDs**: Default subnet IDs are used.
- **Security Group IDs**:
  - **Inbound Rules:** Type = Custom TCP, Port Range = 0-5439, Source = 0.0.0.0/0
  - **Outbound Rules:** Type = Custom TCP, Port Range = 0-5432, Destination = 0.0.0.0/0

---

## **Overview of EMR Serverless Workflow**
The pipeline consists of the following steps:

1. **Create an EMR Serverless Application**
2. **Start the EMR Serverless Application**
3. **Run a PySpark Job**
4. **Stop the EMR Serverless Application**
The workflow is defined using AWS Step Functions, ensuring each step is executed in sequence and handles errors gracefully.

![EMR SERVERLESS](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/EMR_serverless_application.jpg)

*Figure: EMR SERVERLESS*

## **Step Function Workflow**
Below is a breakdown of the Step Function workflow:


SubnetIDS and Security Group IDs I have provided defaults values
### **1. EMR Serverless CreateApplication**
- **Type:** Task
- **Resource:** `arn:aws:states:::emr-serverless:createApplication.sync`
- **Description:** Creates an EMR Serverless application with the specified configuration.
- **Parameters:**
  - **Name:** `EMR-Step-Function`
  - **ReleaseLabel:** `emr-7.6.0`
  - **Type:** `SPARK`
  - **NetworkConfiguration:**
    - **SubnetIds:** `[subnet-056876a6216ff2208, subnet-0ada8c70d139b9242]`
    - **SecurityGroupIds:** `[sg-01fe3016590dcbdf0, sg-0ebe530c94f18ae5d, sg-00718975f449db9b0]`
  - **ResultPath:** `$.emr`
  - **Next:** `EMR Serverless StartApplication`

![CreateApplication](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/EMR_serverless_application.jpg)

*Figure: Create Application*

### **2. EMR Serverless StartApplication**
- **Type:** Task
- **Resource:** `arn:aws:states:::emr-serverless:startApplication.sync`
- **Parameters:**
  - **ApplicationId.$:** `$.emr.ApplicationId`
- **Next:** `EMR Serverless StartJobRun`

![Start Application](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/EMR_serverless_startapplication.jpg)

*Figure: Start Application*

### **3. EMR Serverless StartJobRun**
- **Type:** Task
- **Resource:** `arn:aws:states:::emr-serverless:startJobRun.sync`
- **Description:** Runs a PySpark job to ingest data from PostgreSQL and store it in S3.
- **Parameters:**
  - **ApplicationId.$:** `$.emr.ApplicationId`
  - **Name:** `My PySpark Job Run`
  - **ExecutionRoleArn:** `arn:aws:iam::537124961883:role/Stepfunction_01`
  - **JobDriver:**
    - **SparkSubmit:**
      - **EntryPoint:** `s3://uexpertlyrecords/script/Sparkscript.py`
      - **SparkSubmitParameters:** `--jars s3://uexpertlyrecords/jar/postgresql-42.7.5.jar --conf spark.hadoop.hive.metastore.client.factory.class=com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory`
  - **ConfigurationOverrides:**
    - **MonitoringConfiguration:**
      - **S3MonitoringConfiguration:**
        - **LogUri:** `s3://uexpertlyrecords/logs/`
- **Next:** `EMR Serverless StopApplication`

![Start Job run](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/EMR_serverless_StartJobrun.jpg)

*Figure: Start Job Run*

### **4. SuccessNotification**
- **Type:** Task  
- **Resource:** `arn:aws:states:::sns:publish`  
- **Description:** Sends an SNS notification upon successful job completion.  
- **Parameters:**  
  - **TopicArn:** `arn:aws:sns:us-east-1:537124961883:StepFunctionDataPipelineNotification`  
  - **Message:** `"Spark Job completed successfully"`  
  - **Subject:** `"Success Notification"`  
- **Next:** `SendMessageToSQS`  

![Success Notification](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/sns_successNotifications.jpg)

*Figure: Success Notification*

### **FailureNotification**
- **Type:** Task  
- **Resource:** `arn:aws:states:::sns:publish`  
- **Description:** Sends an SNS notification if the Spark job fails.  
- **Parameters:**  
  - **TopicArn:** `arn:aws:sns:us-east-1:537124961883:failurejob`  
  - **Message:** `"Spark Job failed"`  
  - **Subject:** `"Failure Notification"`  
- **End:** `true`  

---

## **Amazon EventBridge:**

![Amazon EventBridge rule](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/Amazon%20eventbridge.jpg)

*Figure: EventBridge rule*

### **Step 1: Specify Schedule Detail**  

1. **Sign in to the AWS Console**  
   - Visit the [AWS EventBridge Scheduler Console](https://console.aws.amazon.com/events/home).  

2. **Create a New Schedule**  
   - Click **Create schedule**.  

3. **Enter Schedule Details**  
   - **Schedule Name**: `stepfunction_datapipeline`  
   - **Description (Optional)**: `Automation task to run StepFunction, EMR Serverless submit Spark job`.  

4. **Select Schedule Group**  
   - Use the **default** group or create a new schedule group.  

5. **Define Schedule Pattern**  
   - **Occurrence**: Choose either **One-time schedule** or **Recurring schedule**.  
   - **Time Zone**: `(UTC-06:00) America/Chicago`.  
   - **Schedule Type**:  
     - **Cron-based schedule**: Runs at a specific time.  
     - **Rate-based schedule**: Runs at a regular rate (e.g., every 10 minutes).  
   - **Cron Expression**:  
     ```
     cron(00 2 1,15 MAR,APRIL,MAY,JUNE ? *)
     ```  

6. **Flexible Time Window (Optional)**  
   - Choose a time window (e.g., **15 minutes**) for flexible scheduling.  

7. **Set Start and End Dates (Optional)**  
   - **Start Date and Time**: Specify if needed.  
   - **End Date and Time**: Specify if needed.  

8. **Proceed to Next Step**  
   - Click **Next** to continue with selecting the target.  
   
## **AWS CLI Command: Create a New Schedule**

``` sh
AWS_REGION="us-east-1"
STATE_MACHINE_ARN="arn:aws:states:us-east-1:537124961883:stateMachine:EMRServerlessStepFunction"
SCHEDULE_NAME="stepfunction_datapipeline"
IAM_ROLE_ARN="arn:aws:iam::537124961883:role/Amazon_EventBridge_Scheduler_SFN"

```

![Specify Schedule Detail](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/Schedule_name_and_description_event.jpg)

*Figure: Specify Schedule Detail*

### **Step 2: Select Target**  

1. **Sign in to the AWS Console**  
   - Visit the [AWS EventBridge Scheduler Console](https://console.aws.amazon.com/events/home).  

2. **Choose Target for the Schedule**  
   - In the **Select Target** step, choose the API that will be triggered by the schedule.  

3. **Select AWS Step Functions**  
   - Under **Target API**, choose **AWS Step Functions → StartExecution**.  

4. **Configure State Machine**  
   - **State Machine**: `EMRServerlessStepFunction`.  
   - **Create New State Machine**: *(Optional, if needed)*.  
   - **Configure Version/Alias**: *(Optional)*.  

5. **Provide Input Data (Optional)**  
   - Add JSON input for execution (if required). Example:  
     ```json
     {
       "input": {
         "first_name": "test"
       }
     }
     ```
   - If no input is required, use empty braces `{}`.  

6. **Proceed to Next Step**  
   - Click **Next** to configure additional settings.  

## **AWS CLI Command: Choose Target for the Schedule**
``` sh
aws scheduler create-schedule \
    --name "$SCHEDULE_NAME" \
    --schedule-expression "cron(0 2 1,15 MAR,APR,MAY,JUN ? *)" \
    --schedule-expression-timezone "America/Chicago" \
    --flexible-time-window "Mode=FLEXIBLE, MaximumWindowInMinutes=10" \
    --target "Arn=$STATE_MACHINE_ARN, RoleArn=$IAM_ROLE_ARN, Input=\"{}\"" \
    --state ENABLED \
    --action-after-completion NONE \
    --retry-policy "MaximumEventAgeInSeconds=86400, MaximumRetryAttempts=185" \
    --region "$AWS_REGION"
```

![Select Target](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/select%20target.jpg)

*Figure: Select Target*

### **Step 3: Configure Settings (Optional)**  

1. **Enable Schedule**  
   - Check the **Enable schedule** option to activate the schedule immediately.  
   - If unchecked, the schedule can be enabled later after creation.  

2. **Action After Schedule Completion**  
   - Choose **NONE** (default) to keep the schedule after completion.  
   - Select **DELETE** if you want EventBridge Scheduler to remove the schedule once all invocations are completed.  

3. **Retry Policy**  
   - **Maximum Age of Event**: Set to **24 hours** (default).  
   - **Retry Attempts**: Maximum retry attempts set to **185 times** (default).  

4. **Dead-Letter Queue (DLQ) (Optional)**  
   - Choose **None** (default) or configure an Amazon SQS queue for failed event deliveries.  
   - You can select an SQS queue from your AWS account or specify one from another AWS account.  

5. **Encryption Settings**  
   - Default encryption is managed by AWS using AWS-owned keys.  
   - Select **Customize encryption settings** (optional) for advanced encryption control.  

6. **Permissions**  
   - Choose how EventBridge Scheduler gets permissions to invoke the target:  
     - **Create a new role**: AWS will generate a role automatically.  
     - **Use an existing role**: Select a predefined IAM role.  
   - Default role name: `Amazon_EventBridge_Scheduler_SFN_fa1502d6ec`.  
   - Click **Go to IAM console** if you need to modify role permissions.  

7. **Proceed to Next Step**  
   - Click **Next** to review and create the schedule.  

## **AWS CLI Command: Configure Settings**
``` sh
aws scheduler list-schedules --region "$AWS_REGION"

```
![Configure Settings](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/setting_create_schedule_event.jpg)

*Figure: Configure Settings*

### **Step 4: Review and Create Schedule**  
 **Review Schedule Details**
``` sh 
aws scheduler get-schedule --name "$SCHEDULE_NAME" --region "$AWS_REGION"
```
![Review and Create Schedule](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/review%20schedule_event.jpg)

*Figure: Review and Create Schedule*

---

## **Deployment Steps**
1. **Upload Files to S3:**
   - Upload the PostgreSQL JDBC driver and PySpark script to the appropriate S3 locations.
2. **Create the Step Function:**
   - Use the provided JSON definition to create the Step Function in the AWS Management Console or AWS CLI.
3. **Execute the Step Function:**
   - Start the Step Function to trigger the workflow using the following AWS CLI commands:


```sh
aws stepfunctions create-state-machine --name "EMRServerlessStepFunction" \
--role-arn "arn:aws:iam::537124961883:role/Stepfunction_01" \
--definition file://"C:\Users\kasir\Downloads\EMR Serverless_StepFunction Stepfunction.json"

aws stepfunctions start-execution --state-machine-arn "arn:aws:states:us-east-1:537124961883:stateMachine:EMRServerlessStepFunction"

aws stepfunctions list-executions --state-machine-arn "arn:aws:states:us-east-1:537124961883:stateMachine:EMRServerlessStepFunction"
```


---


## **Output**
- The processed data is stored in `s3://uexpertlyrecords/raw-layer/`.

![S3 Bucket](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/Raw_layer.jpg)

*Figure: S3 Bucket*

---

- EMR logs are stored in `s3://uexpertlyrecords/logs/`.

![Logs](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/Bucket_Logs.jpg)

*Figure: S3 Bucket logs*

---

- If EMR Serverless is succeeded then you will see the green and you will recevied message notificaiton to your subscribed mail.

![Succeded](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/EMR_serverless_success.jpg)

*Figure: Succeded*

![ Mail notification success](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/Success%20notification%20spark%20job%20success.jpg)

*Figure: Mail notification success*

---

- If EMR Serverless is failure then you will see the green and you will recevied message notificaiton to your subscribed mail.

![Failure](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/SQSnotificationFailure.jpg)

*Figure: Failure*

![ Mail notification failure](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/AWS%20notification%20message%20job%20failed.jpg)

*Figure: Mail notification failures*

---

- After creating an EventBridge scheduler task, your task will continue running unless you disable it in the scheduler. You can check the execution list in the Step Functions state machine.

![Execution list](https://raw.githubusercontent.com/chaithanyakasi27/Data-Lake-Ingestion-Pipeline-/refs/heads/main/project%20images/state_machine_job_executions_list.jpg)

*Figure: Execution list*

---

**Addtional Resource:**

[Orchestrate Amazon EMR serverless job with AWS step function](https://medium.com/@sathishkrishnan007/orchestrate-amazon-emr-serverless-jobs-with-aws-step-functions-a031d5362fe6)

[Orchestate Amazon EMR Serverless Amazon Documentation](https://aws.amazon.com/blogs/big-data/orchestrate-amazon-emr-serverless-jobs-with-aws-step-functions/)

[Amazon EventBridge Documentation](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html)

[Amazon SNS Documentation](https://docs.aws.amazon.com/sns/latest/dg/subscribe-sqs-queue-to-sns-topic.html)
