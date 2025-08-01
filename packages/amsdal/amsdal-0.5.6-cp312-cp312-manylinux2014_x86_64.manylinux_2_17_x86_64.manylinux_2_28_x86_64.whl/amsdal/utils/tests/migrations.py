import contextlib

from amsdal_data.connections.historical.schema_version_manager import AsyncHistoricalSchemaVersionManager
from amsdal_data.connections.historical.schema_version_manager import HistoricalSchemaVersionManager
from amsdal_models.migration import migrations
from amsdal_models.migration.executors.default_executor import DefaultAsyncMigrationExecutor
from amsdal_models.migration.executors.default_executor import DefaultMigrationExecutor
from amsdal_models.migration.file_migration_executor import SimpleFileMigrationExecutorManager
from amsdal_models.migration.file_migration_generator import SimpleFileMigrationGenerator
from amsdal_models.migration.file_migration_writer import FileMigrationWriter
from amsdal_models.migration.migrations import MigrateData
from amsdal_models.migration.migrations import MigrationSchemas
from amsdal_models.migration.migrations_loader import MigrationsLoader
from amsdal_models.migration.utils import contrib_to_module_root_path
from amsdal_models.schemas.class_schema_loader import ClassSchemaLoader
from amsdal_utils.models.enums import ModuleType

from amsdal.configs.constants import CORE_MIGRATIONS_PATH
from amsdal.configs.main import settings


def migrate() -> None:
    schemas = MigrationSchemas()
    executor = DefaultMigrationExecutor(schemas, use_foreign_keys=True)

    with contextlib.suppress(Exception):
        HistoricalSchemaVersionManager().object_classes  # noqa: B018

    _migrate_per_loader(
        executor,
        MigrationsLoader(
            migrations_dir=CORE_MIGRATIONS_PATH,
            module_type=ModuleType.CORE,
        ),
    )

    for contrib in settings.CONTRIBS:
        contrib_root_path = contrib_to_module_root_path(contrib)
        _migrate_per_loader(
            executor,
            MigrationsLoader(
                migrations_dir=contrib_root_path / settings.MIGRATIONS_DIRECTORY_NAME,
                module_type=ModuleType.CONTRIB,
                module_name=contrib,
            ),
        )

    user_schema_loader = ClassSchemaLoader(
        settings.USER_MODELS_MODULE,
        class_filter=lambda cls: cls.__module_type__ == ModuleType.USER,
    )
    _schemas, _cycle_schemas = user_schema_loader.load_sorted()
    _schemas_map = {_schema.title: _schema for _schema in _schemas}

    for object_schema in _schemas:
        for _operation_data in SimpleFileMigrationGenerator.build_operations(
            ModuleType.USER,
            object_schema,
            None,
        ):
            _operation_name = FileMigrationWriter.operation_name_map[_operation_data.type]
            _operation = getattr(migrations, _operation_name)(
                module_type=ModuleType.USER,
                class_name=_operation_data.class_name,
                new_schema=_operation_data.new_schema.model_dump(),
            )

            _operation.forward(executor)

    for object_schema in _cycle_schemas:
        for _operation_data in SimpleFileMigrationGenerator.build_operations(
            ModuleType.USER,
            object_schema,
            _schemas_map[object_schema.title],
        ):
            _operation_name = FileMigrationWriter.operation_name_map[_operation_data.type]
            _operation = getattr(migrations, _operation_name)(
                module_type=ModuleType.USER,
                class_name=_operation_data.class_name,
                new_schema=_operation_data.new_schema.model_dump(),
            )

            _operation.forward(executor)

    executor.flush_buffer()


def _migrate_per_loader(executor: DefaultMigrationExecutor, loader: MigrationsLoader) -> None:
    for _migration in loader:
        migration_class = SimpleFileMigrationExecutorManager.get_migration_class(_migration)
        migration_class_instance = migration_class()

        for _operation in migration_class_instance.operations:
            if isinstance(_operation, MigrateData):
                executor.flush_buffer()

            _operation.forward(executor)

        executor.flush_buffer()


async def async_migrate() -> None:
    schemas = MigrationSchemas()
    executor = DefaultAsyncMigrationExecutor(schemas)

    with contextlib.suppress(Exception):
        await AsyncHistoricalSchemaVersionManager().object_classes

    await _async_migrate_per_loader(
        executor,
        MigrationsLoader(
            migrations_dir=CORE_MIGRATIONS_PATH,
            module_type=ModuleType.CORE,
        ),
    )

    for contrib in settings.CONTRIBS:
        contrib_root_path = contrib_to_module_root_path(contrib)
        await _async_migrate_per_loader(
            executor,
            MigrationsLoader(
                migrations_dir=contrib_root_path / settings.MIGRATIONS_DIRECTORY_NAME,
                module_type=ModuleType.CONTRIB,
                module_name=contrib,
            ),
        )

    user_schema_loader = ClassSchemaLoader(
        settings.USER_MODELS_MODULE,
        class_filter=lambda cls: cls.__module_type__ == ModuleType.USER,
    )
    _schemas, _cycle_schemas = user_schema_loader.load_sorted()
    _schemas_map = {_schema.title: _schema for _schema in _schemas}

    for object_schema in _schemas:
        for _operation_data in SimpleFileMigrationGenerator.build_operations(
            ModuleType.USER,
            object_schema,
            None,
        ):
            _operation_name = FileMigrationWriter.operation_name_map[_operation_data.type]
            _operation = getattr(migrations, _operation_name)(
                module_type=ModuleType.USER,
                class_name=_operation_data.class_name,
                new_schema=_operation_data.new_schema.model_dump(),
            )

            _operation.forward(executor)

    for object_schema in _cycle_schemas:
        for _operation_data in SimpleFileMigrationGenerator.build_operations(
            ModuleType.USER,
            object_schema,
            _schemas_map[object_schema.title],
        ):
            _operation_name = FileMigrationWriter.operation_name_map[_operation_data.type]
            _operation = getattr(migrations, _operation_name)(
                module_type=ModuleType.USER,
                class_name=_operation_data.class_name,
                new_schema=_operation_data.new_schema.model_dump(),
            )

            _operation.forward(executor)

    await executor.flush_buffer()


async def _async_migrate_per_loader(executor: DefaultAsyncMigrationExecutor, loader: MigrationsLoader) -> None:
    for _migration in loader:
        migration_class = SimpleFileMigrationExecutorManager.get_migration_class(_migration)
        migration_class_instance = migration_class()

        for _operation in migration_class_instance.operations:
            if isinstance(_operation, MigrateData):
                await executor.flush_buffer()

            _operation.forward(executor)

        await executor.flush_buffer()
