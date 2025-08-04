from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest
from dishka import AsyncContainer, Container

from liman_core.llm_node import LLMNode
from liman_core.node import Node
from liman_core.node_actor import NodeActorState
from liman_core.node_actor.actor import NodeActor
from liman_core.node_actor.errors import NodeActorError
from liman_core.tool_node import ToolNode


@pytest.fixture(scope="function")
def real_node(test_containers: tuple[Container, AsyncContainer]) -> Node:
    """
    Create a real Node instance for integration testing
    """
    node_dict = {
        "kind": "Node",
        "name": "SyncIntegrationTestNode",
        "func": "test_function",
        "description": {"en": "Test node for sync integration"},
    }
    node = Node.from_dict(node_dict)
    node.compile()
    return node


@pytest.fixture(scope="function")
def real_llm_node(test_containers: tuple[Container, AsyncContainer]) -> LLMNode:
    """
    Create a real LLMNode instance for integration testing
    """
    node_dict = {
        "kind": "LLMNode",
        "name": "SyncIntegrationLLMNode",
        "prompts": {"system": {"en": "You are a helpful assistant."}},
    }
    node = LLMNode.from_dict(node_dict)
    node.compile()
    return node


@pytest.fixture(scope="function")
def real_tool_node(
    test_containers: tuple[Container, AsyncContainer],
) -> ToolNode | None:
    """
    Create a real ToolNode instance for integration testing
    """
    node_dict = {
        "kind": "ToolNode",
        "name": "SyncIntegrationToolNode",
        "tools": [{"name": "test_tool", "description": "A test tool"}],
    }
    try:
        node = ToolNode.from_dict(node_dict)
        node.compile()
        return node
    except Exception:
        pytest.skip("ToolNode dependencies not available")


def test_sync_actor_factory_pattern(real_node: Node) -> None:
    custom_id: UUID = uuid4()
    mock_llm = Mock()

    sync_actor = NodeActor.create(node=real_node, actor_id=custom_id, llm=mock_llm)

    assert sync_actor.id == custom_id
    assert sync_actor.node is real_node
    assert sync_actor.llm is mock_llm


def test_sync_actor_composite_id_format(real_node: Node) -> None:
    actor_id: UUID = uuid4()
    sync_actor = NodeActor(node=real_node, actor_id=actor_id)

    sync_composite = sync_actor.composite_id
    sync_parts = sync_composite.split("/")

    assert len(sync_parts) == 4
    assert sync_parts[0] == "node_actor"
    assert sync_parts[1] == "node"
    assert sync_parts[2] == "SyncIntegrationTestNode"
    assert sync_parts[3] == str(actor_id)


def test_sync_actor_status_format(real_node: Node) -> None:
    sync_actor = NodeActor(node=real_node)

    sync_status = sync_actor.get_status()

    expected_keys = {"actor_id", "node_name", "node_type", "state", "is_shutdown"}
    assert set(sync_status.keys()) == expected_keys
    assert sync_status["node_name"] == "SyncIntegrationTestNode"
    assert sync_status["node_type"] == "Node"
    assert sync_status["state"] == NodeActorState.IDLE


def test_sync_actor_lifecycle(real_node: Node) -> None:
    sync_actor = NodeActor(node=real_node)

    assert sync_actor.state == NodeActorState.IDLE

    sync_actor.initialize()
    assert sync_actor.state == NodeActorState.READY

    sync_actor.shutdown()
    assert sync_actor.state == NodeActorState.SHUTDOWN


def test_sync_actor_execution_context(real_node: Node) -> None:
    execution_id: UUID = uuid4()
    context = {"custom_key": "custom_value"}

    sync_actor = NodeActor(node=real_node)
    sync_ctx = sync_actor._prepare_execution_context(context, execution_id)

    assert sync_ctx["custom_key"] == "custom_value"
    assert sync_ctx["actor_id"] == sync_actor.id
    assert sync_ctx["execution_id"] == execution_id
    assert sync_ctx["node_name"] == "SyncIntegrationTestNode"
    assert sync_ctx["node_type"] == "Node"


def test_sync_actor_validation_consistency(real_llm_node: LLMNode) -> None:
    sync_actor = NodeActor(node=real_llm_node)

    with pytest.raises(NodeActorError):
        sync_actor._validate_requirements()

    # Should pass validation with LLM
    mock_llm = Mock()
    sync_actor_with_llm = NodeActor(node=real_llm_node, llm=mock_llm)
    sync_actor_with_llm._validate_requirements()  # Should not raise


def test_sync_actor_node_type_detection(
    real_node: Node, real_llm_node: LLMNode
) -> None:
    sync_actor = NodeActor(node=real_node)

    assert not sync_actor.node.is_llm_node
    assert not sync_actor.node.is_tool_node

    sync_llm_actor = NodeActor(node=real_llm_node)

    assert sync_llm_actor.node.is_llm_node
    assert not sync_llm_actor.node.is_tool_node


def test_sync_actor_repr_consistency(real_node: Node) -> None:
    actor_id: UUID = uuid4()
    sync_actor = NodeActor(node=real_node, actor_id=actor_id)

    sync_repr = repr(sync_actor)

    assert str(actor_id) in sync_repr
    assert "SyncIntegrationTestNode" in sync_repr
    assert NodeActorState.IDLE in sync_repr
    assert "NodeActor" in sync_repr


def test_sync_actor_multiple_instances(real_node: Node) -> None:
    actors = [
        NodeActor(node=real_node),
        NodeActor(node=real_node),
        NodeActor(node=real_node),
    ]

    # Initialize all
    for actor in actors:
        actor.initialize()

    # All should be ready
    for actor in actors:
        assert actor.state == NodeActorState.READY

    # Shutdown all
    for actor in actors:
        actor.shutdown()

    # All should be shutdown
    for actor in actors:
        assert actor.state == NodeActorState.SHUTDOWN
