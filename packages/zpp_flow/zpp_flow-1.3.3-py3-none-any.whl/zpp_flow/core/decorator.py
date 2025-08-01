def make_decorator(flag_key):
    def decorator_func(*args, **kwargs):
        inject = {flag_key: True}
        # Récupérer name s'il y en a (pour fusionner)
        name = kwargs.get('name')

        if len(args) == 1 and callable(args[0]):
            func = args[0]
            func._taskflow_decorators = getattr(func, '_taskflow_decorators', [])

            if name is not None:
                # Chercher un décorateur avec même flag_key ET même name
                for d in func._taskflow_decorators:
                    if d.get(flag_key) and d.get('name') == name:
                        # Fusionner kwargs (inject + d), inject l'emporte
                        d.update(kwargs)
                        break
                else:
                    # Pas trouvé, ajouter un nouveau
                    new_inject = {flag_key: True}
                    new_inject.update(kwargs)
                    func._taskflow_decorators.append(new_inject)

            else:
                # Pas de name, on ajoute simplement
                inject.update(kwargs)
                func._taskflow_decorators.append(inject)

            #print(f"[decorator] func={func.__name__} decorators={func._taskflow_decorators}")  # <-- debug
            return func
        else:
            def wrapper(func):
                func._taskflow_decorators = getattr(func, '_taskflow_decorators', [])

                if name is not None:
                    for d in func._taskflow_decorators:
                        if d.get(flag_key) and d.get('name') == name:
                            d.update(kwargs)
                            break
                    else:
                        new_inject = {flag_key: True}
                        new_inject.update(kwargs)
                        func._taskflow_decorators.append(new_inject)
                else:
                    inject_local = inject.copy()
                    inject_local.update(kwargs)
                    func._taskflow_decorators.append(inject_local)

                #print(f"[decorator wrapper] func={func.__name__} decorators={func._taskflow_decorators}")  # <-- debug
                return func
            return wrapper
    return decorator_func


task = make_decorator('is_task')
flow = make_decorator('is_flow')
