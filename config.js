// Global (self-hosted) config. nuget.registryUrls restricts NuGet lookups to a private feed
// (a local mock on 127.0.0.1:8099 in this reproduction).
module.exports = {
  platform: 'local',
  requireConfig: 'optional',
  onboarding: false,
  extends: [':disableDependencyDashboard'],
  nuget: {
    registryUrls: ['http://127.0.0.1:8099/v3/index.json'],
  },
};
