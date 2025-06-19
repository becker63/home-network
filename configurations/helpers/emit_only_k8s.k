
schema EmitConfig:
    objs: [any]
    emit: bool = option(key="emit_non_kubernetes", type='bool', default="False", required=False)


emit_if_set = lambda cfg: EmitConfig -> [any] {
    # Emit the object if flag is true, else emit nothing
    [cfg.objs] if cfg.emit else []
}