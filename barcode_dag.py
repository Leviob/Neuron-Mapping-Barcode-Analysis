from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from find_barcodes import find_barcodes

default_args = {
    'owner': 'leviob',
    'depends_on_past':False,
    'start_date': datetime.now() - timedelta(hours=10),
    'retries': 3,
    'retry_delay': timedelta(hours=1),
    'catchup':False
}

dag = DAG('barcode_dag',
          default_args=default_args,
          description='Load sequencing data and output true barcodes with Airflow',
        )

begin_processing = DummyOperator(task_id='Begin_execution',  dag=dag)

transform_and_load_data = PythonOperator(
    task_id='transform_and_load_data',
    dag=dag,
    python_callable=find_barcodes,
    op_kwargs={
        'input_file': Path('/home/pi/Neuron-Mapping-Barcode-Analysis/data_100K.fastq'),
        'anchor': 'GTACTGCGGCCGCTACCTA',
        'cell_count': 500,
        'error_hamming_distance': 1,
        'proportion_to_consider': 1,
        'output_directory': None,
    },
)

begin_processing >> transform_and_load_data
