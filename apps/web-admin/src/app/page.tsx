'use client'

import { useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useServerStore, useAnalyticsStore } from '@/lib/store'
import { Activity, Server, Settings, BarChart3, Users, Zap } from 'lucide-react'

export default function Dashboard() {
  const { servers, templates, loading, fetchServers, fetchTemplates } = useServerStore()
  const { analytics, fetchAnalytics } = useAnalyticsStore()

  useEffect(() => {
    fetchServers()
    fetchTemplates()
    fetchAnalytics('24h')
  }, [fetchServers, fetchTemplates, fetchAnalytics])

  const stats = [
    {
      title: 'Active Servers',
      value: servers.filter(s => s.enabled).length,
      total: servers.length,
      icon: Server,
      color: 'text-blue-600'
    },
    {
      title: 'Total Templates',
      value: templates.length,
      total: templates.length,
      icon: Settings,
      color: 'text-green-600'
    },
    {
      title: 'Usage Events (24h)',
      value: analytics.length,
      total: analytics.length,
      icon: Activity,
      color: 'text-purple-600'
    },
    {
      title: 'System Health',
      value: '98.5%',
      total: '100%',
      icon: Zap,
      color: 'text-orange-600'
    }
  ]

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <div className="flex items-center space-x-2">
            <Button>
              <Server className="mr-2 h-4 w-4" />
              Add Server
            </Button>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat, index) => {
            const Icon = stat.icon
            return (
              <Card key={index}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    {stat.title}
                  </CardTitle>
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <p className="text-xs text-muted-foreground">
                    {stat.total !== stat.value && `of ${stat.total}`}
                  </p>
                </CardContent>
              </Card>
            )
          })}
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
          <Card className="col-span-4">
            <CardHeader>
              <CardTitle>Virtual Servers</CardTitle>
              <CardDescription>
                Manage your MCP gateway virtual servers
              </CardDescription>
            </CardHeader>
            <CardContent className="pl-2">
              {loading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : (
                <div className="space-y-4">
                  {servers.slice(0, 5).map((server) => (
                    <div
                      key={server.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="flex items-center space-x-4">
                        <Server className="h-8 w-8 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{server.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {server.tools.length} tools
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant={server.enabled ? "default" : "outline"}
                          size="sm"
                        >
                          {server.enabled ? "Enabled" : "Disabled"}
                        </Button>
                      </div>
                    </div>
                  ))}
                  {servers.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      No servers configured yet
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="col-span-3">
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Latest system events and usage
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.slice(0, 5).map((event, index) => (
                  <div key={index} className="flex items-center space-x-4">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {event.action}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
                {analytics.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No recent activity
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Server Templates</CardTitle>
              <CardDescription>
                Available server templates for quick deployment
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {templates.slice(0, 3).map((template) => (
                  <div
                    key={template.id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div>
                      <p className="font-medium">{template.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {template.category} • {template.tools.length} tools
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      Use Template
                    </Button>
                  </div>
                ))}
                {templates.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No templates available
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>System Overview</CardTitle>
              <CardDescription>
                Gateway performance and health metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Gateway Status</span>
                  <span className="text-sm text-green-600">Healthy</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Response Time</span>
                  <span className="text-sm">45ms</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Memory Usage</span>
                  <span className="text-sm">256MB / 512MB</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Active Connections</span>
                  <span className="text-sm">12</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Uptime</span>
                  <span className="text-sm">99.9%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
    </div>
  )
}
