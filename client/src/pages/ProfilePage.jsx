/**
 * ProfilePage — premium profile card design
 */
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../context/authStore'
import { Mail, Calendar, User as UserIcon, LogOut, CheckCircle2, Loader2, Award } from 'lucide-react'
import toast from 'react-hot-toast'

function getInitials(firstName, lastName) {
  if (!firstName && !lastName) return 'U'
  return `${firstName?.charAt(0) || ''}${lastName?.charAt(0) || ''}`.toUpperCase()
}

function formatDate(dateString) {
  if (!dateString) return 'Unknown'
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date)
}

export default function ProfilePage() {
  const { user, fetchCurrentUser, logout } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    async function loadData() {
      if (!user) {
        const result = await fetchCurrentUser()
        if (!result.success) {
          toast.error('Session expired. Please log in again.')
          navigate('/login')
        }
      }
      setLoading(false)
    }
    loadData()
  }, [user, fetchCurrentUser, navigate])

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  if (loading) {
    return (
      <div className="profile-page flex items-center justify-center min-h-[60vh]">
        <Loader2 size={32} className="auth-spinner text-blue-500" />
      </div>
    )
  }

  if (!user) return null

  const initials = getInitials(user.firstName, user.lastName)

  return (
    <div className="profile-page">
      <div className="profile-header">
        <h1 className="profile-title">Your Profile</h1>
        <p className="profile-subtitle">Manage your account settings and preferences</p>
      </div>

      <div className="profile-card">
        <div className="profile-cover">
          <div className="profile-avatar-wrapper">
            {user.avatarUrl ? (
              <img src={user.avatarUrl} alt="Avatar" className="profile-avatar-img" />
            ) : (
              <div className="profile-avatar-initials">{initials}</div>
            )}
            {user.isVerified && (
              <div className="profile-verified-badge" title="Verified Account">
                <CheckCircle2 size={16} />
              </div>
            )}
          </div>
        </div>

        <div className="profile-body">
          <div className="profile-name-row">
            <div>
              <h2 className="profile-name">
                {user.firstName} {user.lastName}
              </h2>
              <p className="profile-username">@{user.username}</p>
            </div>
            <div className="profile-role-badge">
              {user.role}
            </div>
          </div>

          <div className="profile-grid">
            <div className="profile-info-block">
              <div className="profile-info-icon">
                <Mail size={20} />
              </div>
              <div className="profile-info-content">
                <h4>Email Address</h4>
                <p>{user.email}</p>
              </div>
            </div>

            <div className="profile-info-block">
              <div className="profile-info-icon">
                <Calendar size={20} />
              </div>
              <div className="profile-info-content">
                <h4>Member Since</h4>
                <p>{formatDate(user.createdAt)}</p>
              </div>
            </div>

            <div className="profile-info-block">
              <div className="profile-info-icon">
                <UserIcon size={20} />
              </div>
              <div className="profile-info-content">
                <h4>Account Status</h4>
                <p className={user.isActive ? 'text-emerald-400' : 'text-red-400'}>
                  {user.isActive ? 'Active' : 'Inactive'}
                </p>
              </div>
            </div>

            <div className="profile-info-block">
              <div className="profile-info-icon">
                <Award size={20} />
              </div>
              <div className="profile-info-content">
                <h4>Verification</h4>
                <p className={user.isVerified ? 'text-emerald-400' : 'text-slate-400'}>
                  {user.isVerified ? 'Verified' : 'Unverified'}
                </p>
              </div>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-white/10 flex justify-end gap-4">
            <button className="profile-edit-btn" onClick={() => toast.success('Edit feature coming soon!')}>
              Edit Profile
            </button>
            <button className="profile-logout-btn max-w-[140px]" onClick={handleLogout}>
              <LogOut size={16} />
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
