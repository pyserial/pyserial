from android.content import Context

android_context: Context = None


def set_android_context(context: Context) -> None:
    global android_context
    android_context = context


def get_android_context() -> Context:
    global android_context
    return android_context
