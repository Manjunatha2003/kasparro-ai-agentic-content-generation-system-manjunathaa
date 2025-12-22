import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from orchestrator import PipelineOrchestrator, RecoverableError, NonRecoverableError

def test_orchestrator_distinguishes_recoverable_errors():
    orchestrator = PipelineOrchestrator()
    
    with pytest.raises(RecoverableError):
        raise RecoverableError("This can be retried")

def test_orchestrator_distinguishes_non_recoverable_errors():
    orchestrator = PipelineOrchestrator()
    
    with pytest.raises(NonRecoverableError):
        raise NonRecoverableError("This cannot be retried")

@patch('orchestrator.ChatGoogleGenerativeAI')
@patch('orchestrator.Config')
def test_orchestrator_handles_initialization_failure(mock_config, mock_llm):
    mock_config.validate.side_effect = Exception("Config invalid")
    
    orchestrator = PipelineOrchestrator()
    
    with pytest.raises(NonRecoverableError):
        orchestrator.initialize_agents()

@patch('orchestrator.Path')
def test_orchestrator_handles_missing_input(mock_path):
    mock_path.return_value.exists.return_value = False
    
    orchestrator = PipelineOrchestrator()
    
    with pytest.raises(NonRecoverableError):
        orchestrator.load_input("nonexistent.json")

@patch.object(PipelineOrchestrator, 'question_agent')
def test_orchestrator_enforces_faq_count_hard_gate(mock_question_agent):
    orchestrator = PipelineOrchestrator()
    orchestrator.quality_enforcer = Mock()
    
    mock_question_agent.execute.return_value = [
        {"question": f"Q{i}", "answer": f"A{i}", "category": "informational"}
        for i in range(10)
    ]
    
    with pytest.raises(NonRecoverableError) as exc_info:
        orchestrator.generate_questions({})
    
    assert "must be exactly 15" in str(exc_info.value)

@patch.object(PipelineOrchestrator, 'cleanup_outputs')
def test_orchestrator_cleans_outputs_on_non_recoverable_error(mock_cleanup):
    orchestrator = PipelineOrchestrator()
    
    with patch.object(orchestrator, 'initialize_agents', side_effect=NonRecoverableError("Init failed")):
        result = orchestrator.run("input.json")
    
    assert result is False
    mock_cleanup.assert_called_once()

def test_orchestrator_retries_on_recoverable_error():
    orchestrator = PipelineOrchestrator()
    orchestrator.quality_enforcer = Mock()
    orchestrator.question_agent = Mock()
    
    attempt_count = [0]
    
    def side_effect_generator(*args):
        attempt_count[0] += 1
        if attempt_count[0] < 2:
            raise RecoverableError("Try again")
        return [
            {"question": f"Q{i}", "answer": f"A{i}", "category": "informational", "quality_score": 80}
            for i in range(15)
        ]
    
    orchestrator.question_agent.execute.side_effect = side_effect_generator
    orchestrator.quality_enforcer.deduplicate_questions.side_effect = lambda x: x
    orchestrator.quality_enforcer.score_questions.side_effect = lambda x: x
    
    with patch.object(orchestrator, 'initialize_agents'):
        with patch.object(orchestrator, 'load_input', return_value={}):
            with patch.object(orchestrator, 'parse_product', return_value={}):
                with patch.object(orchestrator, 'generate_blocks', return_value={}):
                    with patch.object(orchestrator, 'generate_comparison', return_value=({}, {})):
                        with patch.object(orchestrator, 'assemble_outputs'):
                            result = orchestrator.run("input.json")
    
    assert attempt_count[0] >= 2

def test_orchestrator_fails_after_max_recoverable_attempts():
    orchestrator = PipelineOrchestrator()
    orchestrator.quality_enforcer = Mock()
    orchestrator.question_agent = Mock()
    
    orchestrator.question_agent.execute.side_effect = RecoverableError("Always fails")
    
    with patch.object(orchestrator, 'initialize_agents'):
        with patch.object(orchestrator, 'load_input', return_value={}):
            with patch.object(orchestrator, 'parse_product', return_value={}):
                result = orchestrator.run("input.json")
    
    assert result is False

def test_orchestrator_cleanup_removes_all_output_files(tmp_path):
    orchestrator = PipelineOrchestrator()
    
    output_files = [
        tmp_path / "faq.json",
        tmp_path / "product.json",
        tmp_path / "comparison.json"
    ]
    
    for f in output_files:
        f.write_text('{"test": "data"}')
        assert f.exists()
    
    orchestrator.output_files = [str(f) for f in output_files]
    orchestrator.cleanup_outputs()
    
    for f in output_files:
        assert not f.exists()