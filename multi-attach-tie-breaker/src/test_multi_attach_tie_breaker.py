import pytest
from unittest.mock import MagicMock, patch
from kubernetes.client.rest import ApiException

from multi_attach_tie_breaker import watch_k8s_events, delete_volume_attachment, WorkloadMatcher

@pytest.fixture
def mock_config():
    with patch('multi_attach_tie_breaker.config.load_incluster_config') as mock_config:
        yield mock_config

@pytest.fixture
def mock_watch():
    with patch('multi_attach_tie_breaker.watch.Watch') as mock_watch:
        yield mock_watch

@pytest.fixture
def mock_api_client():
    with patch('multi_attach_tie_breaker.client.CoreV1Api') as mock_api_client:
        yield mock_api_client.return_value

def test_delete_volume_attachment_success(mock_api_client, mock_config):
    mock_api_client.delete_namespaced_persistent_volume_claim.return_value = None
    delete_volume_attachment(mock_api_client, 'test_volume', 'test_pod', "default")
    mock_api_client.delete_namespaced_persistent_volume_claim.assert_called_once_with(
        name='test_volume',
        namespace='default'
    )

def test_delete_volume_attachment_failure(mock_api_client, mock_config):
    mock_api_client.delete_namespaced_persistent_volume_claim.side_effect = ApiException(status=404)
    delete_volume_attachment(mock_api_client, 'test_volume', 'test_pod', 'default')
    mock_api_client.delete_namespaced_persistent_volume_claim.assert_called_once_with(
        name='test_volume',
        namespace='default'
    )
    
def test_workload_matcher():
    workload_matcher = WorkloadMatcher(workload_regexes=['test-re'])
    assert workload_matcher.match('test-regex') == True
    assert workload_matcher.match('not-rest-regex') == False
    assert workload_matcher.match('dummy-test-regex') == True

def test_watch_k8s_events(mock_watch, mock_api_client, mock_config):
    mock_watch_instance = MagicMock()
    mock_watch.return_value = mock_watch_instance
    
    # let's create too mock objects
    object1 = MagicMock()
    object1.message = 'multi-attach error'
    object1.involved_object.name = 'test_volume'
    object1.involved_object.namespace = 'test'
    
    object2 = MagicMock()
    object2.message = 'Normal event'
    

    # Mock events
    mock_event1 = {'type': 'Warning', 'object': object1}
    mock_event2 = {'type': 'Normal', 'object': object2}
    
    # Set up mock event stream
    mock_watch_instance.stream.return_value = [mock_event1, mock_event2]

    # Run the function
    watch_k8s_events()

    # Check if delete_volume_attachment was called
    mock_api_client.delete_namespaced_persistent_volume_claim.assert_called_once_with(
        name='test_volume',
        namespace='test'
    )
    
def test_watch_k8s_events_with_workload_matcher(mock_watch, mock_api_client, mock_config):
    mock_watch_instance = MagicMock()
    mock_watch.return_value = mock_watch_instance
    
    # let's create too mock objects
    object1 = MagicMock()
    object1.message = 'multi-attach error'
    object1.involved_object.name = 'test_volume'
    object1.involved_object.namespace = 'test'
    object1.involved_object.field_selector.split.return_value = ['pod', 'testing_pod']
    
    object2 = MagicMock()
    object2.message = 'Normal event'
    

    # Mock events
    mock_event1 = {'type': 'Warning', 'object': object1}
    mock_event2 = {'type': 'Normal', 'object': object2}
    
    # Set up mock event stream
    mock_watch_instance.stream.return_value = [mock_event1, mock_event2]

    # Run the function
    watch_k8s_events(workload_matcher=WorkloadMatcher(workload_regexes=['test']))
    
    # Check if delete_volume_attachment was called
    mock_api_client.delete_namespaced_persistent_volume_claim.assert_called_once_with(
        name='test_volume',
        namespace='test'
    )
