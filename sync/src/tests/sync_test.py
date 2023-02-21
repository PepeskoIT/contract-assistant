import pytest
from sync import runner


@pytest.mark.asyncio
async def test_runner():
    assert await runner() == []
