"""
@file test_transaction.py
@description Unit tests for transaction management and rollback in note_manager.
@author Daniel
@created 2024-06-10
@lastModified 2024-06-10
@dependencies pytest, document_manager.note_manager.repositories.transaction
"""

import pytest
from document_manager.note_manager.repositories.transaction import UnitOfWork, TransactionError

def test_commit_success():
    uow = UnitOfWork()
    state = {"value": 0}
    def op1():
        state["value"] += 1
    def rb1():
        state["value"] -= 1
    uow.add_operation(op1, rb1)
    uow.commit()
    assert state["value"] == 1

def test_rollback_on_failure():
    uow = UnitOfWork()
    state = {"value": 0}
    def op1():
        state["value"] += 1
    def rb1():
        state["value"] -= 1
    def op2():
        raise Exception("fail")
    def rb2():
        state["value"] -= 10
    uow.add_operation(op1, rb1)
    uow.add_operation(op2, rb2)
    with pytest.raises(TransactionError):
        uow.commit()
    assert state["value"] == -10  # rb2 should have been called first, then rb1 (but only rb2 affects state) 