from typing import Literal

from pydantic import BaseModel

from .base import EndPointKit, api

FileType = Literal["file", "docx", "bitable", "folder", "doc", "sheet", "mindnote", "shortcut", "slides"]


class RootMeta(BaseModel):
    id: str
    token: str
    user_id: str


class FolderMeta(BaseModel):
    id: str
    name: str
    token: str
    createUid: str
    editUid: str
    parentId: str
    ownUid: str


class DeleteResp(BaseModel):
    task_id: str


class CreateFolderBody(BaseModel):
    name: str
    folder_token: str


class CreateFolderResp(BaseModel):
    token: str
    url: str


class Files(EndPointKit):
    @api("/drive/explorer/v2/root_folder/meta")
    def root_meta(self) -> RootMeta:
        """
        https://open.larksuite.com/document/server-docs/docs/drive-v1/folder/get-root-folder-meta
        :return:
        """
        pass

    @api("/drive/explorer/v2/root_folder/meta")
    async def aroot_meta(self) -> RootMeta: ...

    @api("/drive/explorer/v2/folder/:folderToken/meta")
    def folder_meta(self, folderToken: str) -> FolderMeta:
        """
        获取文件夹元信息
        :see https://open.larksuite.com/document/server-docs/docs/drive-v1/folder/get-folder-meta

        :param folderToken:
        :return:
        """

    @api("/drive/explorer/v2/folder/:folderToken/meta")
    async def afolder_meta(self, folderToken: str) -> FolderMeta: ...

    @api("/drive/v1/files/:file_token", method="DELETE")
    def delete(self, file_token: str, type: FileType) -> DeleteResp:
        """
        删除文件/文件夹
        :see https://open.larkoffice.com/document/server-docs/docs/drive-v1/file/delete

        :param file_token:
        :param type:
        :return:
        """

    @api("/drive/v1/files/:file_token", method="DELETE")
    async def adelete(self, file_token: str, type: FileType) -> DeleteResp: ...

    @api("/drive/v1/files/create_folder", method="POST")
    def create_folder(self, body: CreateFolderBody) -> CreateFolderResp:
        """
        创建文件夹
        https://open.larkoffice.com/document/server-docs/docs/drive-v1/folder/create_folder?appId=cli_9faa5e0071b6500c
        :param name:
        :param folder_token:
        :return:
        """

    @api("/drive/v1/files/create_folder", method="POST")
    async def acreate_folder(self, body: CreateFolderBody) -> CreateFolderResp: ...
