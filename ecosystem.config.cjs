const instanceName = process.env.INSTANCE_NAME;
if (!instanceName) throw new Error("INSTANCE_NAME is undefined");

module.exports = {
  apps: [
    {
      name: `${instanceName}-queue-workers`,
      script: "./scripts/python-module.sh queue_worker_supervisor",
      kill_timeout: 60000,
      env: {
        PYTHON_ENV: "production",
        PYTHON_APP_INSTANCE: instanceName,
      },
    },
  ],
}
