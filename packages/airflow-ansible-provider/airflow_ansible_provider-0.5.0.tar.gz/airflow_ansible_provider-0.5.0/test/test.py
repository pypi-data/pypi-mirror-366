import ansible_runner


def run_ansible_playbook(playbook_path, inventory_path, extra_vars=None):
    # 配置 ansible_runner 参数
    runner_config = ansible_runner.runner_config.RunnerConfig(
        private_data_dir="/tmp/ansible_runner",
        playbook=playbook_path,
        inventory=inventory_path,
        extravars=extra_vars,
        verbosity=3,  # 设置更高的详细级别以输出更多信息
    )
    runner_config.prepare()

    # 输出将要运行的命令
    command = runner_config.command
    print("将要运行的命令:", " ".join(command))

    # 如果需要实际运行命令，可以取消注释以下行
    # result = ansible_runner.run(runner_config=runner_config)
    # return result


# 示例调用
playbook_path = "site.yml"
inventory_path = "inventory"
extra_vars = {"var1": "value1"}

run_ansible_playbook(playbook_path, inventory_path, extra_vars)
