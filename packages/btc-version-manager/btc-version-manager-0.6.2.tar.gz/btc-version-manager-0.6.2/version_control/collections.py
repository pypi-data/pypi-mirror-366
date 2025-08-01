class ModelObjectChangeApp:
    """
    A collection for app names
    """

    ADMIN = "admin"

    ITEMS = (ADMIN,)

    CHOICES = ((ADMIN, "Админ-панель"),)


class ModelObjectChangeType:
    """
    A collection for change types.
    """

    OBJECT_CHANGED = "object_changed"
    OBJECT_CREATED = "object_created"
    OBJECT_DELETED = "object_deleted"
    OBJECT_RESTORED = "object_restored"
    OBJECT_STATE_INIT = "object_state_init"

    ITEMS = (
        OBJECT_CHANGED,
        OBJECT_CREATED,
        OBJECT_DELETED,
        OBJECT_RESTORED,
        OBJECT_STATE_INIT,
    )

    CRUD_CHOICES = (
        (OBJECT_CHANGED, "Изменено"),
        (OBJECT_CREATED, "Создано"),
        (OBJECT_DELETED, "Удалено"),
    )

    CHOICES = (
        (OBJECT_CHANGED, "Изменено"),
        (OBJECT_CREATED, "Создано"),
        (OBJECT_DELETED, "Удалено"),
        (OBJECT_RESTORED, "Восстановлено"),
        (OBJECT_STATE_INIT, "Инициализировано состояние"),
    )

    @staticmethod
    def get_type(change_type: str) -> str:
        return dict(ModelObjectChangeType.CHOICES).get(change_type, change_type)
