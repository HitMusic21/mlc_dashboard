/**
 * DashboardLayoutEditor Component
 *
 * Allows users to customize their dashboard layout.
 * Features:
 * - Add/remove widgets
 * - Adjust widget position and size
 * - Preview layout changes
 * - Save/reset layout configuration
 */

import React, { useState, useEffect } from 'react';
import { usePreferencesStore } from '../../stores/usePreferencesStore';
import type { DashboardLayoutConfig, DashboardWidget } from '../../types/preferences';
import '../../styles/components/DashboardLayoutEditor.css';

interface DashboardLayoutEditorProps {
  isOpen: boolean;
  onClose: () => void;
}

const AVAILABLE_WIDGETS = [
  { type: 'stat', label: 'Statistics Cards', icon: '📊' },
  { type: 'chart', label: 'Charts Panel', icon: '📈' },
  { type: 'activity', label: 'Activity Feed', icon: '📋' },
  { type: 'searches', label: 'Saved Searches', icon: '🔍' },
  { type: 'notifications', label: 'Notifications', icon: '🔔' },
] as const;

const DashboardLayoutEditor: React.FC<DashboardLayoutEditorProps> = ({ isOpen, onClose }) => {
  const { preferences, updateDashboardLayout, isLoading } = usePreferencesStore();

  const [widgets, setWidgets] = useState<DashboardWidget[]>([]);
  const [hasChanges, setHasChanges] = useState(false);

  // Initialize from preferences
  useEffect(() => {
    if (preferences?.dashboard_layout?.widgets) {
      setWidgets(preferences.dashboard_layout.widgets);
    } else {
      // Default layout
      setWidgets([
        {
          id: 'stat-1',
          type: 'stat',
          position: { x: 0, y: 0, w: 12, h: 1 },
        },
        {
          id: 'chart-1',
          type: 'chart',
          position: { x: 0, y: 1, w: 8, h: 2 },
        },
        {
          id: 'activity-1',
          type: 'activity',
          position: { x: 8, y: 1, w: 4, h: 2 },
        },
      ]);
    }
  }, [preferences]);

  // Track changes
  useEffect(() => {
    if (preferences?.dashboard_layout?.widgets) {
      const changed = JSON.stringify(widgets) !== JSON.stringify(preferences.dashboard_layout.widgets);
      setHasChanges(changed);
    } else {
      setHasChanges(widgets.length > 0);
    }
  }, [widgets, preferences]);

  // Close on Escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        handleCancel();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen]);

  const addWidget = (type: DashboardWidget['type']) => {
    const existingCount = widgets.filter((w) => w.type === type).length;
    const newWidget: DashboardWidget = {
      id: `${type}-${existingCount + 1}`,
      type,
      position: {
        x: 0,
        y: widgets.length > 0 ? Math.max(...widgets.map((w) => w.position.y + w.position.h)) : 0,
        w: type === 'stat' ? 12 : type === 'chart' ? 8 : 4,
        h: type === 'stat' ? 1 : 2,
      },
    };
    setWidgets([...widgets, newWidget]);
  };

  const removeWidget = (widgetId: string) => {
    setWidgets(widgets.filter((w) => w.id !== widgetId));
  };

  const updateWidget = (widgetId: string, updates: Partial<DashboardWidget>) => {
    setWidgets(
      widgets.map((w) =>
        w.id === widgetId
          ? {
              ...w,
              ...updates,
              position: { ...w.position, ...(updates.position || {}) },
            }
          : w
      )
    );
  };

  const handleSave = async () => {
    try {
      const layout: DashboardLayoutConfig = {
        widgets,
        columns: 12,
      };
      await updateDashboardLayout(layout);
      onClose();
    } catch (error) {
      console.error('Failed to save layout:', error);
    }
  };

  const handleCancel = () => {
    // Reset to current preferences
    if (preferences?.dashboard_layout?.widgets) {
      setWidgets(preferences.dashboard_layout.widgets);
    }
    onClose();
  };

  const handleReset = () => {
    // Reset to default layout
    setWidgets([
      {
        id: 'stat-1',
        type: 'stat',
        position: { x: 0, y: 0, w: 12, h: 1 },
      },
      {
        id: 'chart-1',
        type: 'chart',
        position: { x: 0, y: 1, w: 8, h: 2 },
      },
      {
        id: 'activity-1',
        type: 'activity',
        position: { x: 8, y: 1, w: 4, h: 2 },
      },
    ]);
  };

  const moveWidget = (widgetId: string, direction: 'up' | 'down') => {
    const index = widgets.findIndex((w) => w.id === widgetId);
    if (index === -1) return;

    const newWidgets = [...widgets];
    if (direction === 'up' && index > 0) {
      [newWidgets[index], newWidgets[index - 1]] = [newWidgets[index - 1], newWidgets[index]];
    } else if (direction === 'down' && index < widgets.length - 1) {
      [newWidgets[index], newWidgets[index + 1]] = [newWidgets[index + 1], newWidgets[index]];
    }
    setWidgets(newWidgets);
  };

  const getWidgetLabel = (type: DashboardWidget['type']) => {
    return AVAILABLE_WIDGETS.find((w) => w.type === type)?.label || type;
  };

  const getWidgetIcon = (type: DashboardWidget['type']) => {
    return AVAILABLE_WIDGETS.find((w) => w.type === type)?.icon || '📦';
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={handleCancel}>
      <div className="layout-editor modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <h2 className="modal-title">Dashboard Layout</h2>
          <button
            type="button"
            className="btn btn-ghost btn-sm layout-editor__close"
            onClick={handleCancel}
            aria-label="Close"
          >
            <svg viewBox="0 0 20 20" fill="currentColor" width="20" height="20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="modal-body">
          {/* Available Widgets */}
          <div className="layout-editor__section">
            <h3 className="layout-editor__section-title">Available Widgets</h3>
            <div className="layout-editor__widget-palette">
              {AVAILABLE_WIDGETS.map((widget) => (
                <button
                  key={widget.type}
                  type="button"
                  className="layout-editor__widget-palette-item"
                  onClick={() => addWidget(widget.type)}
                >
                  <span className="layout-editor__widget-icon">{widget.icon}</span>
                  <span className="layout-editor__widget-label">{widget.label}</span>
                  <span className="layout-editor__add-icon">+</span>
                </button>
              ))}
            </div>
          </div>

          <div className="divider" />

          {/* Current Layout */}
          <div className="layout-editor__section">
            <div className="layout-editor__section-header">
              <h3 className="layout-editor__section-title">Current Layout</h3>
              {widgets.length > 0 && (
                <button type="button" className="btn btn-ghost btn-sm" onClick={handleReset}>
                  Reset to Default
                </button>
              )}
            </div>

            {widgets.length === 0 ? (
              <div className="layout-editor__empty">
                <p className="text-secondary">No widgets added yet. Add widgets from above to customize your dashboard.</p>
              </div>
            ) : (
              <div className="layout-editor__widget-list">
                {widgets.map((widget, index) => (
                  <div key={widget.id} className="layout-editor__widget-item">
                    <div className="layout-editor__widget-info">
                      <span className="layout-editor__widget-icon">{getWidgetIcon(widget.type)}</span>
                      <div>
                        <div className="layout-editor__widget-name">{getWidgetLabel(widget.type)}</div>
                        <div className="layout-editor__widget-size">
                          Width: {widget.position.w} cols, Height: {widget.position.h} rows
                        </div>
                      </div>
                    </div>

                    <div className="layout-editor__widget-actions">
                      {/* Move buttons */}
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        onClick={() => moveWidget(widget.id, 'up')}
                        disabled={index === 0}
                        aria-label="Move up"
                      >
                        <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                          <path
                            fillRule="evenodd"
                            d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </button>
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        onClick={() => moveWidget(widget.id, 'down')}
                        disabled={index === widgets.length - 1}
                        aria-label="Move down"
                      >
                        <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                          <path
                            fillRule="evenodd"
                            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </button>

                      {/* Width controls */}
                      <select
                        className="select select-sm"
                        value={widget.position.w}
                        onChange={(e) =>
                          updateWidget(widget.id, {
                            position: { ...widget.position, w: Number(e.target.value) },
                          })
                        }
                      >
                        <option value={3}>3 cols</option>
                        <option value={4}>4 cols</option>
                        <option value={6}>6 cols</option>
                        <option value={8}>8 cols</option>
                        <option value={12}>12 cols</option>
                      </select>

                      {/* Remove button */}
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm text-error"
                        onClick={() => removeWidget(widget.id)}
                        aria-label="Remove widget"
                      >
                        <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                          <path
                            fillRule="evenodd"
                            d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button type="button" className="btn btn-secondary" onClick={handleCancel}>
            Cancel
          </button>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleSave}
            disabled={!hasChanges || isLoading}
          >
            {isLoading ? 'Saving...' : 'Save Layout'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DashboardLayoutEditor;
