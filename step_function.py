from stepfunctions.steps import (Chain, TrainingStep, ModelStep, EndpointConfigStep, EndpointStep)
from stepfunctions.workflow import Workflow
from stepfunctions.inputs import ExecutionInput
from sagemaker.amazon.amazon_estimator import image_uris
from sagemaker.estimator import Estimator
from sagemaker.inputs import TrainingInput
import os
import uuid

def build_sf():
    workflow_execution_role = os.environ['WORKFLOW_EXECUTION_ROLE']
    training_instance = os.environ['TRAINING_INSTANCE']
    region = os.environ['REGION']
    estimator_role = os.environ['ESTIMATOR_ROLE']  
    hosting_instance = os.environ['HOSTING_INSTANCE']
    artifact_location = os.environ['ARTIFACT_LOCATION']
    data_location = os.environ['DATA_LOCATION']

    image_uri = image_uris.retrieve(region = region, framework='ipinsights')

    hyperparameters={
                    'num_entity_vectors':'10',
                    'vector_dim':'128',
                    'epoch' : '1'
                    }

    ip_insights = Estimator(
            image_uri = image_uri,
            instance_type = training_instance,
            instance_count = 1,
            role = estimator_role,
            use_spot_instances = True,
            max_run = 300,
            max_wait = 360,
            hyperparameters = hyperparameters
    )              

    execution_input = ExecutionInput(schema ={
        'JobName': str, 
        'ModelName': str,
        'ArtifactLocation' : str,
        'EndpointName': str,
        'DataLocation': str
        
    })

    train_input = TrainingInput(
        execution_input['DataLocation'], distribution='FullyReplicated', content_type='text/csv'
    )

    input_data = {
        'train': train_input
    }

    train_step = TrainingStep(
        'Training Model', 
        estimator=ip_insights,
        data= input_data,
        job_name=execution_input['JobName'],
        output_data_config_path = execution_input['ArtifactLocation']
    )

    model_step = ModelStep(
        'Saving model',
        model=train_step.get_expected_model(),
        model_name=execution_input['ModelName'],
        instance_type=training_instance
    )

    endpoint_config_step = EndpointConfigStep(
        'Creating Endpoint Config',
        endpoint_config_name=execution_input['ModelName'],
        model_name=execution_input['ModelName'],
        initial_instance_count=1,
        instance_type=hosting_instance
    )

    endpoint_step = EndpointStep(
        'Creating Endpoint',
        endpoint_name=execution_input['EndpointName'],
        endpoint_config_name=execution_input['ModelName']
    )

    workflow_definition = Chain([
        train_step,
        model_step,
        endpoint_config_step,
        endpoint_step
    ])

    workflow_name = 'Workflow-Ip-Insights-{}'.format(uuid.uuid1().hex)
    
    workflow = Workflow(
        name=workflow_name,
        definition=workflow_definition,
        role=workflow_execution_role
    )

    workflow.create()

    workflow.execute(
            inputs={
                    'JobName': 'IPInsights-{}'.format(uuid.uuid1().hex), 
                    'ModelName': 'IPInsights-{}'.format(uuid.uuid1().hex), 
                    'ArtifactLocation': artifact_location + '{}'.format(uuid.uuid1().hex),   
                    'EndpointName': 'IPInsights-{}'.format(uuid.uuid1().hex),   
                    'DataLocation': data_location
            }
        )

if __name__ == '__main__':
    build_sf()