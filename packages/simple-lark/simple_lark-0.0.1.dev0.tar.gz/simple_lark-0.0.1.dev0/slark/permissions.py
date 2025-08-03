from typing import Literal

from pydantic import BaseModel, RootModel

from .base import EndPointKit, api
from .files import FileType

PermKind = Literal["view", "edit", "full_access"]


class AddMemberReq(BaseModel):
    member_type: Literal[
        "email", "openid", "unionid", "openchat", "opendepartmentid", "userid", "groupid", "wikispaceid"
    ] = "openid"
    member_id: str
    perm: PermKind
    perm_type: Literal["container", "single_page"] = "container"
    type: (
        Literal[
            "user", "chat", "department", "group", "wiki_space_member", "wiki_space_viewer", "wiki_space_editor", ""
        ]
        | None
    ) = None


class MemberAdded(BaseModel):
    member_type: str
    member_id: str
    perm: str
    perm_type: str
    type: str | None = None


class AddMemberResp(BaseModel):
    member: MemberAdded


BatchAddMemberReq = RootModel[list[RootModel]]
BatchAddMemberResp = RootModel[list[AddMemberResp]]


class Permissions(EndPointKit):
    @api("/drive/v1/permissions/:token/members")
    def _add_member(
        self, token: str, type: FileType, body: AddMemberReq, need_notification: Literal["true", "false"] = "false"
    ) -> AddMemberResp: ...

    def add_member(
        self, token: str, type: FileType, body: AddMemberReq, need_notification: bool = False
    ) -> AddMemberResp:
        """
        新增权限
        https://open.larkoffice.com/document/server-docs/docs/permission/permission-member/create

        :param token:
        :param type:
        :param body:
        :param need_notification:
        :return:
        """
        return self._add_member(token, type, body, "true" if need_notification else "false")

    @api("/drive/v1/permissions/:token/members/batch_create")
    def batch_add_member(
        self, token: str, type: FileType, body: BatchAddMemberReq, need_notification: Literal["true", "false"] = "false"
    ) -> BatchAddMemberResp:
        """
        批量新增权限
        :param token:
        :param type:
        :param body:
        :param need_notification:
        :return:
        """
