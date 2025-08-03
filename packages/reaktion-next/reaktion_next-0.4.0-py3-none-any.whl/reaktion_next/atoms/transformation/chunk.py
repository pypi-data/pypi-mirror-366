import asyncio
from typing import List
from reaktion_next.atoms.combination.base import CombinationAtom
from reaktion_next.events import (
    CompleteOutEvent,
    ErrorOutEvent,
    EventType,
    NextOutEvent,
    OutEvent,
)
import logging

logger = logging.getLogger(__name__)


class ChunkAtom(CombinationAtom):
    complete: List[bool] = [False, False]

    async def run(self):
        iterations = self.set_values.get("iterations", 1)
        sleep = self.set_values.get("sleep", None)
        iteration_sleep = self.set_values.get("iteration_sleep", None)

        try:
            while True:
                event = await self.get()

                if event.type == EventType.ERROR:
                    await self.transport.put(
                        ErrorOutEvent(
                            handle="return_0",
                            exception=event.exception,
                            source=self.node.id,
                            caused_by=[event.current_t],
                        )
                    )
                    break

                if event.type == EventType.NEXT:
                    assert len(event.value) == 1, (
                        "ChunkAtom only supports flattening one value"
                    )

                    assert isinstance(event.value[0], list), (
                        "ChunkAtom only supports flattening lists"
                    )

                    for i in range(iterations):
                        for value in event.value[0]:
                            await self.transport.put(
                                NextOutEvent(
                                    handle="return_0",
                                    value=[value],
                                    source=self.node.id,
                                    caused_by=[event.current_t],
                                )
                            )

                            if sleep:
                                await asyncio.sleep(sleep * 0.001)

                        if (
                            iteration_sleep and i < iterations - 1
                        ):  # don't sleep after last iteration
                            await asyncio.sleep(iteration_sleep * 0.001)

                if event.type == EventType.COMPLETE:
                    await self.transport.put(
                        CompleteOutEvent(
                            handle="return_0",
                            value=[],
                            source=self.node.id,
                            caused_by=[event.current_t],
                        )
                    )
                    break

        except asyncio.CancelledError as e:
            logger.warning(f"Atom {self.node} is getting cancelled")
            raise e

        except Exception as e:
            logger.exception(f"Atom {self.node} excepted")
            raise e
