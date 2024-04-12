import os
from dotenv import load_dotenv

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Load env variables
load_dotenv()

# Set trace provider
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: os.environ["JAEGER_SERVICE_NAME"]})
    )
)
tracer = trace.get_tracer(__name__)

# Create a JaegerExporter
jaeger_exporter = JaegerExporter(
    # configure agent
    agent_host_name=os.environ["JAEGER_HOST"],
    agent_port=int(os.environ["JAEGER_PORT"]),
    udp_split_oversized_batches=True,
)

# Create a BatchSpanProcessor and add the exporter to it
span_processor = BatchSpanProcessor(jaeger_exporter)

# Add to the tracer
trace.get_tracer_provider().add_span_processor(span_processor)
