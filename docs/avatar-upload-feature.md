# Avatar Upload Feature

## Overview
The avatar upload feature allows authenticated users to upload, display, and manage their profile picture. Images are stored on the server's file system and served as static files.

## Backend Implementation

### Database Schema
Added `avatar_url` field to the User model:
- **Type**: `String` (nullable)
- **Stores**: Relative URL path to the avatar image (e.g., `/uploads/avatars/filename.jpg`)
- **Migration**: `alembic/versions/a1b2c3d4e5f6_add_avatar_url_to_user.py`

### Storage Configuration (`app/core/storage.py`)

#### Settings
- **Upload Directory**: `uploads/avatars/`
- **Allowed Formats**: JPG, JPEG, PNG, GIF, WEBP
- **Max File Size**: 5MB
- **Filename Format**: `{user_id}_{uuid}.{ext}`

#### Functions
1. **`validate_image_file(file: UploadFile)`**
   - Validates file extension and content type
   - Raises HTTPException for invalid files

2. **`save_avatar(file: UploadFile, user_id: str) -> str`**
   - Validates the file
   - Generates unique filename
   - Saves to disk
   - Returns URL path

3. **`delete_avatar(avatar_url: Optional[str])`**
   - Deletes avatar file from disk
   - Silently fails if file doesn't exist

### API Endpoints

#### Upload Avatar
```
POST /upload-avatar
Authorization: Bearer {token}
Content-Type: multipart/form-data

Body: file (image file)

Response: UserRead (200 OK)
```

**Features:**
- Deletes old avatar before uploading new one
- Generates unique filename to prevent conflicts
- Updates user record with new avatar URL

#### Delete Avatar
```
DELETE /delete-avatar
Authorization: Bearer {token}

Response: UserRead (200 OK)
```

**Features:**
- Removes avatar file from disk
- Sets `avatar_url` to `null` in database

### Static File Serving (`app/main.py`)
```python
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
```
- Serves uploaded avatars at `/uploads/avatars/{filename}`
- Files accessible via HTTP GET request

## Frontend Implementation

### Type Definitions (`types/auth.ts`)
```typescript
export interface User {
  // ... other fields
  avatar_url: string | null;
}
```

### API Client (`lib/api.ts`)

#### Upload Avatar
```typescript
async uploadAvatar(token: string, file: File): Promise<User>
```

#### Delete Avatar
```typescript
async deleteAvatar(token: string): Promise<User>
```

### Avatar Upload Dialog Component
**Location**: `components/profile/AvatarUploadDialog.tsx`

**Features:**
- File selection with drag-and-drop support
- Live preview of selected image
- Client-side validation (file type, size)
- Upload and delete buttons
- Loading states and error handling
- Toast notifications

**Validation:**
- File types: JPG, PNG, GIF, WEBP
- Max size: 5MB
- Real-time preview before upload

### Profile Page Integration
**Location**: `app/profile/page.tsx`

**Features:**
1. **Avatar Display**
   - Shows uploaded avatar or fallback initials
   - Hover overlay with camera icon
   - Click to open upload dialog

2. **Avatar Management**
   - Upload new avatar
   - Delete existing avatar
   - Automatic refresh after changes

## User Flow

### Uploading an Avatar
1. User navigates to profile page
2. Hovers over avatar → camera icon appears
3. Clicks avatar → upload dialog opens
4. Clicks "Choose Image" → file picker opens
5. Selects image file → preview appears
6. Clicks "Upload" → image uploads
7. Success toast appears → dialog closes
8. Profile page refreshes with new avatar

### Deleting an Avatar
1. User navigates to profile page
2. Clicks avatar → upload dialog opens
3. Clicks "Delete Avatar" button (if avatar exists)
4. Confirmation → avatar deleted
5. Success toast appears → dialog closes
6. Profile page shows fallback initials

## File Structure

### Backend Files
```
app/
├── core/
│   └── storage.py              # Storage utilities
├── models/
│   └── user.py                 # User model with avatar_url
├── routers/
│   └── profile.py              # Avatar endpoints
└── main.py                     # Static file serving

alembic/versions/
└── a1b2c3d4e5f6_add_avatar_url_to_user.py

uploads/avatars/                # Uploaded files (created at runtime)
```

### Frontend Files
```
src/
├── components/profile/
│   ├── AvatarUploadDialog.tsx  # Upload dialog component
│   └── index.ts                # Exports
├── app/profile/
│   └── page.tsx                # Profile page with avatar
├── types/
│   └── auth.ts                 # User type with avatar_url
└── lib/
    └── api.ts                  # API client methods
```

## Security Considerations

1. **File Validation**
   - Client and server-side validation
   - File type whitelist
   - File size limits

2. **Authentication**
   - All endpoints require valid JWT token
   - Users can only upload/delete their own avatar

3. **File Storage**
   - Unique filenames prevent overwriting
   - Old files deleted before new upload
   - Files stored outside web root (served via FastAPI)

4. **Error Handling**
   - Graceful handling of upload failures
   - User-friendly error messages
   - Silent failure for file deletion errors

## Testing

### Manual Testing Steps

#### Test Avatar Upload
1. Start backend: `docker compose up`
2. Start frontend: `cd frontend && npm run dev`
3. Register/login to application
4. Navigate to profile page (`/profile`)
5. Hover over avatar → verify camera icon appears
6. Click avatar → verify dialog opens
7. Click "Choose Image" → select valid image
8. Verify preview appears
9. Click "Upload" → verify success
10. Verify avatar updates on profile page

#### Test Invalid File
1. Open avatar dialog
2. Try to upload:
   - File > 5MB → should show error
   - Non-image file → should show error
   - Unsupported format (.bmp) → should show error

#### Test Avatar Deletion
1. Upload an avatar (follow upload test)
2. Open avatar dialog again
3. Click "Delete Avatar" → verify success
4. Verify fallback initials appear

### API Testing Examples

**Upload Avatar:**
```bash
curl -X POST http://localhost:8000/upload-avatar \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/image.jpg"
```

**Delete Avatar:**
```bash
curl -X DELETE http://localhost:8000/delete-avatar \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Migration Instructions

### Database Migration
Run the migration when the database is available:
```bash
alembic upgrade head
```

This adds the `avatar_url` column to the `user` table.

### Server Setup
Ensure the uploads directory has proper permissions:
```bash
mkdir -p uploads/avatars
chmod 755 uploads/avatars
```

## Troubleshooting

### Issue: Avatars not displaying
- **Check**: Is the uploads directory accessible?
- **Check**: Is the static file mount configured in main.py?
- **Check**: Is the API_BASE_URL correct in frontend?

### Issue: Upload fails with "File too large"
- **Solution**: Reduce image size or increase MAX_FILE_SIZE in storage.py
- **Note**: Also check FastAPI's default request size limit

### Issue: "Permission denied" when saving files
- **Solution**: Ensure uploads directory has write permissions
- **Docker**: May need to adjust volume permissions

## Future Enhancements

1. **Image Processing**
   - Resize/crop images to standard size
   - Generate thumbnails
   - Use Pillow or similar library

2. **Cloud Storage**
   - Support AWS S3, Cloudinary, etc.
   - Better scalability for production

3. **Image Optimization**
   - Compress images automatically
   - Convert to WebP format

4. **CDN Integration**
   - Serve images via CDN
   - Improve load times globally

5. **Avatar Gallery**
   - Provide default avatars to choose from
   - Avatar history/versions
