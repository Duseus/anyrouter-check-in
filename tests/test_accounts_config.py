import json

import pytest

from utils.config import load_accounts_config

ENV_VARS = [
	'ANYROUTER_ACCOUNTS',
	'ANYROUTER_SESSION',
	'ANYROUTER_API_USER',
	'AGENTROUTER_SESSION',
	'AGENTROUTER_API_USER',
]


@pytest.fixture(autouse=True)
def clear_account_env(monkeypatch):
	for name in ENV_VARS:
		monkeypatch.delenv(name, raising=False)


def test_no_accounts_configured_returns_none():
	assert load_accounts_config() is None


def test_json_accounts_only(monkeypatch):
	monkeypatch.setenv('ANYROUTER_ACCOUNTS', json.dumps([{'cookies': {'session': 'abc'}, 'api_user': '1'}]))

	accounts = load_accounts_config()

	assert accounts is not None
	assert len(accounts) == 1
	assert accounts[0].name == 'Account 1'
	assert accounts[0].provider == 'anyrouter'


def test_env_pair_accounts_without_json(monkeypatch):
	monkeypatch.setenv('ANYROUTER_SESSION', 'any-session')
	monkeypatch.setenv('ANYROUTER_API_USER', '123')
	monkeypatch.setenv('AGENTROUTER_SESSION', 'agent-session')
	monkeypatch.setenv('AGENTROUTER_API_USER', '190250')

	accounts = load_accounts_config()

	assert accounts is not None
	assert [(a.name, a.provider, a.cookies, a.api_user) for a in accounts] == [
		('AnyRouter', 'anyrouter', {'session': 'any-session'}, '123'),
		('AgentRouter', 'agentrouter', {'session': 'agent-session'}, '190250'),
	]


def test_empty_json_with_env_pair(monkeypatch):
	monkeypatch.setenv('ANYROUTER_ACCOUNTS', '')
	monkeypatch.setenv('AGENTROUTER_SESSION', 'agent-session')
	monkeypatch.setenv('AGENTROUTER_API_USER', '190250')

	accounts = load_accounts_config()

	assert accounts is not None
	assert len(accounts) == 1
	assert accounts[0].name == 'AgentRouter'
	assert accounts[0].provider == 'agentrouter'


def test_env_pair_merged_after_json_accounts(monkeypatch):
	monkeypatch.setenv(
		'ANYROUTER_ACCOUNTS',
		json.dumps([{'name': 'Main', 'cookies': {'session': 'abc'}, 'api_user': '1'}]),
	)
	monkeypatch.setenv('ANYROUTER_SESSION', 'any-session')
	monkeypatch.setenv('ANYROUTER_API_USER', '123')

	accounts = load_accounts_config()

	assert accounts is not None
	assert [a.name for a in accounts] == ['Main', 'AnyRouter']


def test_incomplete_env_pair_is_skipped(monkeypatch):
	monkeypatch.setenv('AGENTROUTER_API_USER', '190250')

	assert load_accounts_config() is None

	monkeypatch.setenv('ANYROUTER_SESSION', 'any-session')
	monkeypatch.setenv('ANYROUTER_API_USER', '123')

	accounts = load_accounts_config()

	assert accounts is not None
	assert [a.name for a in accounts] == ['AnyRouter']


def test_invalid_json_still_fails_with_env_pair(monkeypatch):
	monkeypatch.setenv('ANYROUTER_ACCOUNTS', '[{bad json}]')
	monkeypatch.setenv('ANYROUTER_SESSION', 'any-session')
	monkeypatch.setenv('ANYROUTER_API_USER', '123')

	assert load_accounts_config() is None
