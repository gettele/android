#include "quickjs.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static void compiles(const char *source, int flags, int expected) {
    JSRuntime *rt = JS_NewRuntime();
    assert(rt);
    JSContext *ctx = JS_NewContext(rt);
    assert(ctx);
    JSValue result = JS_Eval(ctx, source, strlen(source), "<await-using>",
                            flags | JS_EVAL_FLAG_COMPILE_ONLY);
    int actual = !JS_IsException(result);
    if (!actual) {
        JSValue error = JS_GetException(ctx);
        const char *message = JS_ToCString(ctx, error);
        assert(message && strstr(message, "SyntaxError"));
        JS_FreeCString(ctx, message);
        JS_FreeValue(ctx, error);
    }
    if (actual != expected) fprintf(stderr, "unexpected compilation result: %s\n", source);
    assert(actual == expected);
    JS_FreeValue(ctx, result);
    JS_FreeContext(ctx);
    JS_FreeRuntime(rt);
}

int main(void) {
    const int script = JS_EVAL_TYPE_GLOBAL, module = JS_EVAL_TYPE_MODULE;
    compiles("class C { static { for (await using x of []) {} } }", script, 0);
    compiles("class C { static { for (await using x in {}) {} } }", script, 0);
    compiles("function f() { for (await using x of []) {} }", module, 0);
    compiles("class C { static { for (await using x of []) {} } }", module, 0);
    compiles("export function f() { for (await using [a] of []) {} }", module, 0);
    compiles("async function f() { for (await using x of []) {} }", script, 1);
    compiles("(async () => { for (await using x of []) {} })", script, 1);
    compiles("async function* g() { for (await using x of []) {} }", script, 1);
    compiles("for (await using x of []) {}", module, 1);
    compiles("function f() { for (using x of []) {} }", script, 1);
    puts("10 await-using regression cases passed");
    return 0;
}
