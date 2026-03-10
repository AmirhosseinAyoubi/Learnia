/**
 * RegisterPage — premium glassmorphism design
 */
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../context/authStore'
import { BookOpen, Eye, EyeOff, ArrowRight, Loader2, CheckCircle2, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'

function PasswordStrength({ password }) {
  const checks = [
    { label: 'At least 8 characters', ok: password.length >= 8 },
    { label: 'Contains a number', ok: /\d/.test(password) },
    { label: 'Contains uppercase', ok: /[A-Z]/.test(password) },
  ]
  if (!password) return null
  return (
    <ul className="auth-pw-checks">
      {checks.map((c) => (
        <li key={c.label} className={`auth-pw-check ${c.ok ? 'ok' : 'fail'}`}>
          {c.ok ? <CheckCircle2 size={13} /> : <XCircle size={13} />}
          {c.label}
        </li>
      ))}
    </ul>
  )
}

export default function RegisterPage() {
  const [form, setForm] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
  })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const { register } = useAuthStore()
  const navigate = useNavigate()

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (form.password !== form.confirmPassword) {
      toast.error('Passwords do not match')
      return
    }
    if (form.password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }

    setLoading(true)

    const result = await register({
      email: form.email,
      username: form.username,
      password: form.password,
      firstName: form.firstName,
      lastName: form.lastName,
    })

    if (result.success) {
      toast.success('Account created! Welcome to Learnia 🚀')
      navigate('/')
    } else {
      toast.error(result.error || 'Registration failed. Email or username may already be taken.')
    }

    setLoading(false)
  }

  return (
    <div className="auth-page">
      <div className="auth-blob auth-blob-1" />
      <div className="auth-blob auth-blob-2" />
      <div className="auth-blob auth-blob-3" />

      <div className="auth-card auth-card-wide">
        <div className="auth-logo">
          <div className="auth-logo-icon">
            <BookOpen size={28} />
          </div>
          <span className="auth-logo-text">Learnia</span>
        </div>

        <div className="auth-header">
          <h1 className="auth-title">Create your account</h1>
          <p className="auth-subtitle">Join thousands of learners today — it's free</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {/* Name row */}
          <div className="auth-row">
            <div className="auth-field">
              <label className="auth-label" htmlFor="firstName">First name</label>
              <input
                id="firstName"
                name="firstName"
                type="text"
                required
                className="auth-input"
                placeholder="Alice"
                value={form.firstName}
                onChange={handleChange}
              />
            </div>
            <div className="auth-field">
              <label className="auth-label" htmlFor="lastName">Last name</label>
              <input
                id="lastName"
                name="lastName"
                type="text"
                required
                className="auth-input"
                placeholder="Smith"
                value={form.lastName}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="email">Email address</label>
            <input
              id="email"
              name="email"
              type="email"
              required
              autoComplete="email"
              className="auth-input"
              placeholder="you@example.com"
              value={form.email}
              onChange={handleChange}
            />
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="username">Username</label>
            <input
              id="username"
              name="username"
              type="text"
              required
              className="auth-input"
              placeholder="alice_smith"
              value={form.username}
              onChange={handleChange}
            />
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="password">Password</label>
            <div className="auth-input-wrapper">
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                required
                autoComplete="new-password"
                className="auth-input"
                placeholder="••••••••"
                value={form.password}
                onChange={handleChange}
              />
              <button
                type="button"
                className="auth-eye-btn"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            <PasswordStrength password={form.password} />
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="confirmPassword">Confirm password</label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              required
              autoComplete="new-password"
              className="auth-input"
              placeholder="••••••••"
              value={form.confirmPassword}
              onChange={handleChange}
            />
          </div>

          <button type="submit" disabled={loading} className="auth-btn">
            {loading ? (
              <>
                <Loader2 size={18} className="auth-spinner" />
                Creating account…
              </>
            ) : (
              <>
                Create account
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account?{' '}
          <Link to="/login" className="auth-link">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
