import inspect
from unittest.mock import patch

import pytest

from src.chaosinjector import ChaosInjector


class TestClass:
    def method(self):
        return "real_method_result"

    def another_method(self):
        return "another_real"

    attr = "real_attr"


class SlottedClass:
    __slots__ = ["value"]

    def __init__(self):
        self.value = "real_value"


@pytest.fixture
def chaos_injector():
    return ChaosInjector


def test_probability_1_always_real(chaos_injector):
    obj = TestClass()
    chaos_injector.inject(obj, probability=1.0)

    assert obj.method() == "real_method_result"
    assert obj.attr == "real_attr"


def test_probability_0_always_noop(chaos_injector):
    obj = TestClass()
    chaos_injector.inject(obj, probability=0.0)

    assert obj.method() is None
    result = obj.method()
    assert result is None
    assert obj.attr is None


@patch("random.random")
def test_probability_0_5_mocked(mock_random, chaos_injector):
    obj = TestClass()
    chaos_injector.inject(obj, probability=0.5)

    mock_random.return_value = 0.4
    assert obj.method() == "real_method_result"

    mock_random.return_value = 0.6
    result = obj.method()
    assert result is None


def test_decider_always_true(chaos_injector):
    obj = TestClass()
    chaos_injector.inject(obj, decider=lambda name: True)

    assert obj.method() == "real_method_result"
    assert obj.attr == "real_attr"


def test_decider_always_false(chaos_injector):
    obj = TestClass()
    chaos_injector.inject(obj, decider=lambda name: False)

    result = obj.method()
    assert result is None
    assert obj.attr is None


def test_decider_conditional(chaos_injector):
    obj = TestClass()
    chaos_injector.inject(
        obj, decider=lambda name: name == "method"
    )

    assert obj.method() == "real_method_result"
    another_result = obj.another_method()
    assert another_result is None
    assert obj.attr is None


@patch("random.random")
def test_method_probs_specific(mock_random, chaos_injector):
    obj = TestClass()
    chaos_injector.inject(
        obj, method_probs={"method": 1.0, "another_method": 0.0}
    )

    mock_random.return_value = 0.5
    assert obj.method() == "real_method_result"

    another_result = obj.another_method()
    assert another_result is None

    mock_random.return_value = 0.4
    assert obj.attr == "real_attr"

    mock_random.return_value = 0.6
    assert obj.attr is None


@patch("random.random")
def test_method_probs_with_fallback(mock_random, chaos_injector):
    obj = TestClass()
    chaos_injector.inject(obj, probability=0.3, method_probs={"method": 0.8})

    mock_random.return_value = 0.7
    assert obj.method() == "real_method_result"

    mock_random.return_value = 0.9
    result = obj.method()
    assert result is None

    mock_random.return_value = 0.2
    assert obj.another_method() == "another_real"

    mock_random.return_value = 0.4
    another_result = obj.another_method()
    assert another_result is None


def test_non_existing_attribute(chaos_injector):
    obj = TestClass()
    chaos_injector.inject(obj, probability=1.0)

    with pytest.raises(AttributeError):
        obj.non_existing

    chaos_injector.inject(obj, probability=0.0)
    with pytest.raises(AttributeError):
        obj.non_existing


def test_multiple_adds(chaos_injector):
    obj1 = TestClass()
    obj2 = TestClass()

    chaos_injector.inject(obj1, probability=1.0)
    chaos_injector.inject(obj2, probability=0.0)

    assert obj1.method() == "real_method_result"
    assert obj2.method() is None


def test_callable_vs_non_callable(chaos_injector):
    class MixedClass:
        def func(self): return "func"

        prop = "prop"

    obj = MixedClass()
    chaos_injector.inject(obj, probability=0.0)

    func_result = obj.func()
    assert func_result is None
    assert obj.prop is None


def test_decider_priority_over_probs(chaos_injector):
    obj = TestClass()
    chaos_injector.inject(
        obj,
        probability=0.5,
        decider=lambda name: name == "method",
        method_probs={"method": 0.0}
    )

    assert obj.method() == "real_method_result"
    another_result = obj.another_method()
    assert another_result is None


def test_invalid_probability(chaos_injector):
    obj = TestClass()
    with pytest.raises(ValueError):
        chaos_injector.inject(obj, probability=1.5)


def test_create_proxy_probability_1_always_real(chaos_injector):
    obj = TestClass()
    proxy_obj = chaos_injector.create_proxy(obj, probability=1.0)

    assert isinstance(proxy_obj, TestClass)
    assert proxy_obj.method() == "real_method_result"
    assert proxy_obj.attr == "real_attr"


def test_create_proxy_probability_0_always_noop(chaos_injector):
    obj = TestClass()
    proxy_obj = chaos_injector.create_proxy(obj, probability=0.0)

    assert isinstance(proxy_obj, TestClass)
    result = proxy_obj.method()
    assert result is None
    assert proxy_obj.attr is None


@patch("random.random")
def test_create_proxy_probability_0_5_mocked(mock_random, chaos_injector):
    obj = TestClass()
    proxy_obj = chaos_injector.create_proxy(obj, probability=0.5)

    mock_random.return_value = 0.4
    assert proxy_obj.method() == "real_method_result"

    mock_random.return_value = 0.6
    result = proxy_obj.method()
    assert result is None


def test_create_proxy_decider_always_true(chaos_injector):
    obj = TestClass()
    proxy_obj = chaos_injector.create_proxy(obj, decider=lambda name: True)

    assert isinstance(proxy_obj, TestClass)
    assert proxy_obj.method() == "real_method_result"
    assert proxy_obj.attr == "real_attr"


def test_create_proxy_decider_always_false(chaos_injector):
    obj = TestClass()
    proxy_obj = chaos_injector.create_proxy(obj, decider=lambda name: False)

    assert isinstance(proxy_obj, TestClass)
    result = proxy_obj.method()
    assert result is None
    assert proxy_obj.attr is None


def test_create_proxy_decider_conditional(chaos_injector):
    obj = TestClass()
    proxy_obj = chaos_injector.create_proxy(
        obj, decider=lambda name: name == "method"
    )

    assert isinstance(proxy_obj, TestClass)
    assert proxy_obj.method() == "real_method_result"
    another_result = proxy_obj.another_method()
    assert another_result is None
    assert proxy_obj.attr is None


@patch("random.random")
def test_create_proxy_method_probs_specific(mock_random, chaos_injector):
    obj = TestClass()
    proxy_obj = chaos_injector.create_proxy(
        obj, method_probs={
            "method": 1.0, "another_method": 0.0
        }
    )

    mock_random.return_value = 0.5
    assert proxy_obj.method() == "real_method_result"

    another_result = proxy_obj.another_method()
    assert another_result is None

    mock_random.return_value = 0.4
    assert proxy_obj.attr == "real_attr"

    mock_random.return_value = 0.6
    assert proxy_obj.attr is None


@patch("random.random")
def test_create_proxy_method_probs_with_fallback(mock_random, chaos_injector):
    obj = TestClass()
    proxy_obj = chaos_injector.create_proxy(
        obj, probability=0.3, method_probs={"method": 0.8}
    )

    mock_random.return_value = 0.7
    assert proxy_obj.method() == "real_method_result"

    mock_random.return_value = 0.9
    result = proxy_obj.method()
    assert result is None

    mock_random.return_value = 0.2
    assert proxy_obj.another_method() == "another_real"

    mock_random.return_value = 0.4
    another_result = proxy_obj.another_method()
    assert another_result is None


def test_create_proxy_non_existing_attribute(chaos_injector):
    obj = TestClass()
    proxy_obj = chaos_injector.create_proxy(obj, probability=1.0)

    with pytest.raises(AttributeError):
        proxy_obj.non_existing

    proxy_obj = chaos_injector.create_proxy(obj, probability=0.0)
    with pytest.raises(AttributeError):
        proxy_obj.non_existing


def test_create_proxy_callable_vs_non_callable(chaos_injector):
    class MixedClass:
        def func(self): return "func"

        prop = "prop"

    obj = MixedClass()
    proxy_obj = chaos_injector.create_proxy(obj, probability=0.0)

    assert isinstance(proxy_obj, MixedClass)
    func_result = proxy_obj.func()
    assert func_result is None
    assert proxy_obj.prop is None


def test_create_proxy_decider_priority_over_probs(chaos_injector):
    obj = TestClass()
    proxy_obj = chaos_injector.create_proxy(
        obj,
        probability=0.5,
        decider=lambda name: name == "method",
        method_probs={"method": 0.0}
    )

    assert isinstance(proxy_obj, TestClass)
    assert proxy_obj.method() == "real_method_result"
    another_result = proxy_obj.another_method()
    assert another_result is None


def test_create_proxy_invalid_probability(chaos_injector):
    obj = TestClass()
    with pytest.raises(ValueError):
        chaos_injector.create_proxy(obj, probability=1.5)


def test_create_proxy_state_copy_dict(chaos_injector):
    class StateClass:
        def __init__(self):
            self.dynamic_attr = "dynamic_value"

    obj = StateClass()
    proxy_obj = chaos_injector.create_proxy(obj, probability=1.0)

    assert isinstance(proxy_obj, StateClass)
    assert proxy_obj.dynamic_attr == "dynamic_value"


def test_create_proxy_state_copy_slots(chaos_injector):
    slotted_obj = SlottedClass()
    proxy_obj = chaos_injector.create_proxy(slotted_obj, probability=1.0)

    assert isinstance(proxy_obj, SlottedClass)
    assert proxy_obj.value == "real_value"


def test_create_proxy_no_mutation_original(chaos_injector):
    obj = TestClass()
    proxy_obj = chaos_injector.create_proxy(obj, probability=0.0)

    result = proxy_obj.method()
    assert result is None

    assert obj.method() == "real_method_result"


class TestAsyncClass:
    async def async_method(self):
        return "real_async_result"

    def sync_method(self):
        return "real_sync_result"


@pytest.mark.asyncio
async def test_inject_async_method_real(chaos_injector):
    obj = TestAsyncClass()
    chaos_injector.inject(obj, probability=1.0)
    result = await obj.async_method()
    assert result == "real_async_result"
    assert inspect.iscoroutinefunction(obj.async_method)


@pytest.mark.asyncio
async def test_inject_async_method_noop(chaos_injector):
    obj = TestAsyncClass()
    chaos_injector.inject(obj, probability=0.0)
    fake_coro = obj.async_method()
    assert inspect.iscoroutine(fake_coro)
    result = await fake_coro
    assert result is None
    assert obj.sync_method() is None


@pytest.mark.asyncio
async def test_create_proxy_async_method_real(chaos_injector):
    obj = TestAsyncClass()
    proxy_obj = chaos_injector.create_proxy(obj, probability=1.0)
    assert isinstance(proxy_obj, TestAsyncClass)
    result = await proxy_obj.async_method()
    assert result == "real_async_result"


@pytest.mark.asyncio
async def test_create_proxy_async_method_noop(chaos_injector):
    obj = TestAsyncClass()
    proxy_obj = chaos_injector.create_proxy(obj, probability=0.0)
    assert isinstance(proxy_obj, TestAsyncClass)
    fake_coro = proxy_obj.async_method()
    assert inspect.iscoroutine(fake_coro)
    result = await fake_coro
    assert result is None
    original_result = await obj.async_method()
    assert original_result == "real_async_result"


@pytest.mark.asyncio
async def test_mixed_sync_async_noop(chaos_injector):
    obj = TestAsyncClass()
    chaos_injector.inject(obj, probability=0.0)
    fake_async = obj.async_method()
    assert await fake_async is None
    assert obj.sync_method() is None
