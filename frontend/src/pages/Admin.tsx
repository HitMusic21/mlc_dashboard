import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { usePreferencesStore, selectItemsPerPage } from '../stores/usePreferencesStore';
import type { CatalogUpload, UploadStatus } from '../types/catalog';
import type { UserResponse } from '../types/api';

export const Admin: React.FC = () => {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [uploadToDelete, setUploadToDelete] = useState<number | null>(null);
  const limit = usePreferencesStore(selectItemsPerPage);

  // Fetch all users
  const { data: usersResponse } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => apiClient.getUsers(),
  });

  // Fetch all uploads (optionally filtered by user)
  const { data: uploadsResponse, isLoading: uploadsLoading } = useQuery({
    queryKey: ['admin-uploads', page, selectedUserId],
    queryFn: () =>
      apiClient.getAllUploads({
        page,
        limit,
        user_id: selectedUserId || undefined,
      }),
  });

  // Delete upload mutation
  const deleteMutation = useMutation({
    mutationFn: (uploadId: number) => apiClient.deleteUpload(uploadId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-uploads'] });
      setUploadToDelete(null);
    },
  });

  const handleDeleteClick = (uploadId: number) => {
    setUploadToDelete(uploadId);
  };

  const handleConfirmDelete = () => {
    if (uploadToDelete) {
      deleteMutation.mutate(uploadToDelete);
    }
  };

  const handleCancelDelete = () => {
    setUploadToDelete(null);
  };

  const getStatusBadgeClass = (status: UploadStatus) => {
    const baseClass = 'status-badge';
    switch (status) {
      case 'completed':
        return `${baseClass} status-completed`;
      case 'processing':
        return `${baseClass} status-processing`;
      case 'failed':
        return `${baseClass} status-failed`;
      case 'uploading':
        return `${baseClass} status-uploading`;
      default:
        return baseClass;
    }
  };

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1 className="page-title">Admin Dashboard</h1>
        <p className="page-subtitle">Manage users and uploads</p>
      </div>

      {/* User Management Section */}
      <div className="admin-section">
        <div className="section-card">
          <h2 className="section-title">Users</h2>
          {usersResponse && (
            <div className="users-grid">
              <div className="stats-row">
                <div className="stat-item">
                  <span className="stat-label">Total Users</span>
                  <span className="stat-value">
                    {usersResponse.pagination.total_items}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Publishers</span>
                  <span className="stat-value">
                    {
                      usersResponse.data.filter((u: UserResponse) => u.role === 'publisher')
                        .length
                    }
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Admins</span>
                  <span className="stat-value">
                    {usersResponse.data.filter((u: UserResponse) => u.role === 'admin').length}
                  </span>
                </div>
              </div>

              <div className="users-table">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {usersResponse.data.map((user: UserResponse) => (
                      <tr key={user.id}>
                        <td>{user.id}</td>
                        <td>{user.email}</td>
                        <td>
                          <span className={`role-badge role-${user.role}`}>
                            {user.role}
                          </span>
                        </td>
                        <td>
                          <span
                            className={`status-badge ${
                              user.is_active ? 'status-active' : 'status-inactive'
                            }`}
                          >
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td>
                          <button
                            type="button"
                            onClick={() => setSelectedUserId(user.id)}
                            className="button-link"
                          >
                            View Uploads
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Uploads Management Section */}
      <div className="admin-section">
        <div className="section-card">
          <div className="section-header">
            <h2 className="section-title">
              {selectedUserId ? 'User Uploads' : 'All Uploads'}
            </h2>
            {selectedUserId && (
              <button
                type="button"
                onClick={() => setSelectedUserId(null)}
                className="button-secondary"
              >
                Show All Uploads
              </button>
            )}
          </div>

          {uploadsLoading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading uploads...</p>
            </div>
          ) : uploadsResponse ? (
            <>
              <div className="uploads-table">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Filename</th>
                      <th>Publisher</th>
                      <th>User Email</th>
                      <th>Tracks</th>
                      <th>Status</th>
                      <th>Created</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {uploadsResponse.data.map((upload: CatalogUpload) => {
                      const user = usersResponse?.data.find((u: UserResponse) => u.id === upload.user_id);
                      return (
                        <tr key={upload.id}>
                          <td>{upload.id}</td>
                          <td className="filename-cell">
                            <a href={`/results/${upload.id}`}>{upload.filename}</a>
                          </td>
                          <td>{upload.publisher_name}</td>
                          <td>{user?.email || 'Unknown'}</td>
                          <td>{upload.tracks_count || 0}</td>
                        <td>
                          <span className={getStatusBadgeClass(upload.status)}>
                            {upload.status}
                          </span>
                        </td>
                        <td>{new Date(upload.created_at).toLocaleDateString()}</td>
                        <td>
                          <button
                            type="button"
                            onClick={() => handleDeleteClick(upload.id)}
                            className="button-danger-small"
                            disabled={deleteMutation.isPending}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {uploadsResponse.pagination.total_pages > 1 && (
                <div className="pagination">
                  <button
                    type="button"
                    className="pagination-button"
                    onClick={() => setPage(page - 1)}
                    disabled={page === 1 || uploadsLoading}
                  >
                    Previous
                  </button>

                  <div className="pagination-info">
                    Page {page} of {uploadsResponse.pagination.total_pages} (
                    {uploadsResponse.pagination.total_items} total uploads)
                  </div>

                  <button
                    type="button"
                    className="pagination-button"
                    onClick={() => setPage(page + 1)}
                    disabled={page === uploadsResponse.pagination.total_pages || uploadsLoading}
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <p>No uploads found</p>
            </div>
          )}
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {uploadToDelete && (
        <div className="modal-overlay" onClick={handleCancelDelete}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Confirm Delete</h3>
              <button
                type="button"
                className="modal-close"
                onClick={handleCancelDelete}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <div className="modal-body">
              <p>
                Are you sure you want to delete this upload? This action cannot be undone.
              </p>
              <p className="warning-text">
                All match results associated with this upload will also be deleted.
              </p>
            </div>

            <div className="modal-footer">
              <button
                type="button"
                onClick={handleCancelDelete}
                className="button-secondary"
                disabled={deleteMutation.isPending}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmDelete}
                className="button-danger"
                disabled={deleteMutation.isPending}
              >
                {deleteMutation.isPending ? 'Deleting...' : 'Delete Upload'}
              </button>
            </div>

            {deleteMutation.isError && (
              <div className="modal-error">
                Failed to delete upload. Please try again.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
