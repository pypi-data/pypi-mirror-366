from dataclasses import dataclass, field
from typing import ClassVar

from httpx import AsyncClient, HTTPStatusError

from clickup_sdk.common import utilities
from clickup_sdk.core import Settings, models


@dataclass
class Client:
    _BASE_URL: ClassVar[str] = "https://api.clickup.com/"

    http_client: "AsyncClient"
    settings: Settings = field(
        default_factory=Settings,  # type: ignore
    )

    async def get_tasks(
        self,
        list_id: int,
    ) -> models.GetTasksResponse:
        page = 0
        is_last_page = False
        tasks: list[models.Task] = []
        while not is_last_page:
            try:
                response = await self.http_client.get(
                    url=f"{self._BASE_URL}api/v2/list/{list_id}/task",
                    headers={
                        "Authorization": self.settings.AUTHORIZATION,
                    },
                    params={
                        "page": page,
                        "include_closed": True,
                    },
                )
                response.raise_for_status()
            except HTTPStatusError as exc:
                raise exc
            else:
                response_dict: dict = response.json()
                is_last_page = response_dict["last_page"]
                page += 1
                tasks.extend(
                    [
                        models.Task(
                            id=task["id"],
                            name=task["name"],
                            update_date=utilities.microseconds_string_to_date(
                                microseconds_string=task["date_updated"],
                            ),
                            creation_date=utilities.microseconds_string_to_date(
                                microseconds_string=task["date_created"],
                            ),
                            status=task["status"]["status"],
                            start_date=utilities.microseconds_string_to_date(
                                microseconds_string=task["start_date"]
                            ),
                            due_date=utilities.microseconds_string_to_date(
                                microseconds_string=task["due_date"]
                            ),
                            custom_fields=[
                                models.CustomField(
                                    name=custom_field["name"],
                                    value=utilities.get_custom_field_value(
                                        custom_field
                                    ),
                                )
                                for custom_field in task["custom_fields"]
                            ],
                            tags=[
                                models.Tag(
                                    name=tag["name"],
                                )
                                for tag in task["tags"]
                            ],
                        )
                        for task in response_dict["tasks"]
                    ]
                )
        return models.GetTasksResponse(
            tasks=tasks,
        )
