# Password Change Feature

## Overview
The password change feature allows authenticated users to securely update their password by verifying their current password first.

## Backend Implementation

### Endpoint
- **URL**: `POST /change-password`
- **Authentication**: Required (JWT Bearer token)
- **Request Body**:
  ```json
  {
    "current_password": "string",
    "new_password": "string"
  }
  ```
- **Response**: `UserRead` object (200 OK)
- **Error Responses**:
  - `400 Bad Request` - Current password is incorrect
  - `400 Bad Request` - New password must be different from current password
  - `401 Unauthorized` - Invalid or missing authentication token

### Password Validation Rules
New passwords must meet the following requirements:
- Minimum 8 characters
- Maximum 128 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)

### Security Features
1. **Current Password Verification**: Users must provide their current password to change it
2. **Password Comparison**: New password must be different from the current password
3. **Password Hashing**: All passwords are hashed using bcrypt via FastAPI-Users PasswordHelper
4. **Authentication Required**: Only authenticated users can change their password

### Files Modified
- `app/models/user.py`: Added `ChangePasswordRequest` schema
- `app/routers/profile.py`: Added `/change-password` endpoint with verification logic

## Frontend Implementation

### Component
- **Location**: `frontend/src/components/profile/ChangePasswordDialog.tsx`
- **Features**:
  - Current password input field with visibility toggle
  - New password input field with visibility toggle
  - Confirm password input field with visibility toggle
  - Real-time validation with error messages
  - Password requirements displayed to user
  - Loading states during API calls
  - Success/error toast notifications

### Validation
Client-side validation includes:
- Required field validation
- Password strength requirements (matches backend)
- Password confirmation matching
- New password different from current password

### User Flow
1. User clicks "Change Password" button on profile page
2. Modal dialog opens with three password fields
3. User enters current password
4. User enters new password (with requirements displayed)
5. User confirms new password
6. On submit:
   - Validation checks run
   - If valid, API request is made
   - On success: Success toast, form reset, dialog closes
   - On error: Error message displayed (e.g., "Current password is incorrect")

### Files Modified
- `frontend/src/components/profile/ChangePasswordDialog.tsx`: Enhanced with current password field
- `frontend/src/types/auth.ts`: Updated `ChangePasswordRequest` interface
- `frontend/src/lib/api.ts`: Updated API method to use new endpoint

## API Usage Example

### Request
```bash
curl -X POST http://localhost:8000/change-password \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPassword123",
    "new_password": "NewSecurePassword456"
  }'
```

### Success Response (200 OK)
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```

### Error Response (400 Bad Request)
```json
{
  "detail": "Current password is incorrect"
}
```

## Testing

### Manual Testing Steps
1. Start the backend server: `docker compose up`
2. Start the frontend: `cd frontend && npm run dev`
3. Register and login to the application
4. Navigate to profile page
5. Click "Change Password" button
6. Test scenarios:
   - Enter wrong current password (should show error)
   - Enter same password as current (should show error)
   - Enter password not meeting requirements (should show validation errors)
   - Enter valid new password (should succeed)

### Security Considerations
- Current password is always verified before allowing changes
- Passwords are never logged or exposed in responses
- Failed password attempts could be rate-limited (future enhancement)
- Password history could be implemented to prevent reuse (future enhancement)
