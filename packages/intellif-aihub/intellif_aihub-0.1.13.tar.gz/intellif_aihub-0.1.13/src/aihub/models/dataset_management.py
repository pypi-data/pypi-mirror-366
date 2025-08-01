from __future__ import annotations

from enum import IntEnum
from typing import List, Optional

from pydantic import BaseModel, Field


class DatasetVersionStatus(IntEnum):
    """数据集版本状态：1-等待中；2-运行中；3-成功；4-失败；5-加载meta；6-构建index"""
    Waiting = 1  # 等待中
    Running = 2  # 运行中
    Success = 3  # 成功
    Fail = 4  # 失败
    MetaDB = 5  # 加载meta
    BuildIndex = 6  # 构建index


class UploadType(IntEnum):
    """上传类型：1-本地上传；3-服务器路径上传；4-Labelfree；5-数据接入"""
    LOCAL = 1  # 本地上传
    SERVER_PATH = 3  # 服务器路径上传
    LABELFREE = 4  # Labelfree
    DATA_INGEST = 5  # 数据接入


class CreateDatasetRequest(BaseModel):
    """创建数据集请求"""
    name: str = Field(description="数据集名称")
    description: str = Field(description="数据集描述")
    tags: List[int] = Field(description="标签ID列表，通过标签管理系统查询")
    cover_img: Optional[str] = Field(None, alias="cover_img", description="封面图片URL")
    create_by: Optional[int] = Field(None, alias="create_by", description="创建人")
    is_private: Optional[bool] = Field(None, alias="is_private", description="是否私有")
    access_user_ids: Optional[List[int]] = Field(None, alias="access_user_ids", description="具有访问权限的用户ID列表")


class CreateDatasetResponse(BaseModel):
    """创建数据集返回"""
    id: int = Field(alias="id", description="数据集ID")


class DatasetVersionBase(BaseModel):
    """数据集版本概要"""
    id: int = Field(description="版本ID")
    version: int = Field(description="版本号")
    status: DatasetVersionStatus = Field(description="版本状态")
    parquet_index_path: Optional[str] = Field(None, alias="parquet_index_path", description="parquet索引文件路径")
    data_count: int = Field(alias="data_count", description="数量")

    model_config = {"use_enum_values": True}


class DatasetDetail(BaseModel):
    """数据集详情"""
    id: int = Field(description="数据集 ID")
    name: str = Field(description="名称")
    description: str = Field(description="描述")
    cover_img: Optional[str] = Field(None, alias="cover_img", description="封面图片URL")
    created_at: int = Field(alias="created_at", description="创建时间戳 (ms)")
    updated_at: int = Field(alias="update_at", description="更新时间戳 (ms)")
    user_id: int = Field(alias="user_id", description="创建人ID")
    username: str = Field(description="创建人用户名")
    tags: List[int] = Field(description="标签ID列表")
    access_user_ids: Optional[List[int]] = Field(None, alias="access_user_ids", description="可访问的用户ID列表")
    is_private: Optional[bool] = Field(None, alias="is_private", description="是否私有")
    versions: List[DatasetVersionBase] = Field(description="版本列表")


class ExtInfo(BaseModel):
    """扩展信息"""
    rec_file_path: Optional[str] = Field(None, alias="rec_file_path", description="rec文件路径")
    idx_file_path: Optional[str] = Field(None, alias="idx_file_path", description="idx文件路径")
    json_file_path: Optional[str] = Field(None, alias="json_file_path", description="json文件路径")
    image_dir_path: Optional[str] = Field(None, alias="image_dir_path", description="图片目录路径")


class CreateDatasetVersionRequest(BaseModel):
    """创建版本请求"""
    upload_path: str = Field(alias="upload_path", description="上传路径")
    description: Optional[str] = Field(None, description="版本描述")
    dataset_id: int = Field(alias="dataset_id", description="数据集ID")
    object_cnt: Optional[int] = Field(None, alias="object_cnt", description="对象数")
    data_size: Optional[int] = Field(None, alias="data_size", description="数据大小")
    create_by: Optional[int] = Field(None, alias="create_by", description="创建人")
    upload_type: Optional[UploadType] = Field(alias="upload_type", description="上传类型")
    ext_info: Optional[ExtInfo] = Field(None, alias="ext_info", description="扩展文件信息")

    model_config = {"use_enum_values": True}


class CreateDatasetVersionResponse(BaseModel):
    """创建版本返回"""
    id: int = Field(alias="id", description="版本ID")


class UploadDatasetVersionRequest(BaseModel):
    """上传数据集版本请求"""
    upload_path: str = Field(alias="upload_path", description="上传目录")
    upload_type: UploadType = Field(alias="upload_type", description="上传类型")
    dataset_id: int = Field(alias="dataset_id", description="数据集ID")
    parent_version_id: Optional[int] = Field(None, alias="parent_version_id", description="父版本ID")
    description: Optional[str] = Field(None, alias="description", description="版本描述")

    model_config = {"use_enum_values": True}


class UploadDatasetVersionResponse(BaseModel):
    """上传数据集版本返回"""
    id: int = Field(alias="id", description="版本ID")


class DatasetVersionDetail(BaseModel):
    """数据集版本详情"""
    id: int = Field(description="版本ID")
    version: int = Field(description="版本号")
    dataset_id: int = Field(alias="dataset_id", description="数据集ID")
    upload_path: str = Field(alias="upload_path", description="上传路径")
    upload_type: UploadType = Field(alias="upload_type", description="上传类型")
    parent_version_id: Optional[int] = Field(None, alias="parent_version_id", description="父版本ID")
    description: Optional[str] = Field(None, description="版本描述")
    status: DatasetVersionStatus = Field(description="状态")
    message: Optional[str] = Field(None, description="信息")
    created_at: int = Field(alias="created_at", description="创建时间戳 (ms)")
    user_id: int = Field(alias="user_id", description="创建人ID")
    data_size: Optional[int] = Field(None, alias="data_size", description="数据大小")
    data_count: Optional[int] = Field(None, alias="data_count", description="条数")
    parquet_index_path: Optional[str] = Field(None, alias="parquet_index_path", description="parquet索引文件路径")
    ext_info: Optional[ExtInfo] = Field(None, alias="ext_info", description="扩展信息")

    model_config = {"use_enum_values": True}


class FileUploadData(BaseModel):
    """文件上传数据"""
    path: str = Field(description="路径")
    url: str = Field(description="URL")
