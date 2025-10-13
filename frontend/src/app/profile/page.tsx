"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { ProtectedRoute } from "@/components/auth";
import { EditProfileDialog } from "@/components/profile/EditProfileDialog";
import { ChangePasswordDialog } from "@/components/profile/ChangePasswordDialog";
import { AvatarUploadDialog } from "@/components/profile/AvatarUploadDialog";
import {
  MailIcon,
  UserIcon,
  ShieldCheckIcon,
  CalendarIcon,
  EditIcon,
  KeyIcon,
  CameraIcon
} from "lucide-react";
import { API_BASE_URL } from "@/constants";

function ProfileContent() {
  const { user, refreshUser } = useAuth();
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [avatarDialogOpen, setAvatarDialogOpen] = useState(false);

  // Get user initials for avatar
  const getUserInitials = () => {
    if (!user?.username) return "U";
    return user.username.substring(0, 2).toUpperCase();
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header Section */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Profile</h1>
          <p className="text-muted-foreground">Manage your account information and preferences</p>
        </div>

        {/* Profile Overview Card */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
              {/* Avatar */}
              <div className="relative group">
                <Avatar className="h-24 w-24">
                  <AvatarImage
                    src={user?.avatar_url ? `${API_BASE_URL}${user.avatar_url}` : undefined}
                    alt={user?.username}
                  />
                  <AvatarFallback className="text-2xl font-bold bg-primary text-primary-foreground">
                    {getUserInitials()}
                  </AvatarFallback>
                </Avatar>
                <button
                  onClick={() => setAvatarDialogOpen(true)}
                  className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                  aria-label="Change avatar"
                >
                  <CameraIcon className="h-8 w-8 text-white" />
                </button>
              </div>

              {/* User Info */}
              <div className="flex-1 text-center md:text-left">
                <h2 className="text-2xl font-bold mb-1">{user?.username}</h2>
                <p className="text-muted-foreground mb-4">{user?.email}</p>
                <div className="flex flex-wrap gap-2 justify-center md:justify-start">
                  <Badge variant={user?.is_active ? "default" : "secondary"}>
                    {user?.is_active ? "Active" : "Inactive"}
                  </Badge>
                  <Badge variant={user?.is_verified ? "default" : "outline"}>
                    {user?.is_verified ? "Verified" : "Not Verified"}
                  </Badge>
                  {user?.is_superuser && (
                    <Badge variant="destructive">
                      Superuser
                    </Badge>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col gap-2">
                <Button variant="outline" size="sm" onClick={() => setEditDialogOpen(true)}>
                  <EditIcon className="h-4 w-4 mr-2" />
                  Edit Profile
                </Button>
                <Button variant="outline" size="sm" onClick={() => setPasswordDialogOpen(true)}>
                  <KeyIcon className="h-4 w-4 mr-2" />
                  Change Password
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Account Details Grid */}
        <div className="grid gap-6 md:grid-cols-2 mb-6">
          {/* Personal Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserIcon className="h-5 w-5" />
                Personal Information
              </CardTitle>
              <CardDescription>Your personal account details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">Username</label>
                <p className="text-base font-medium mt-1">{user?.username}</p>
              </div>
              <Separator />
              <div>
                <label className="text-sm font-medium text-muted-foreground">Email Address</label>
                <p className="text-base font-medium mt-1 flex items-center gap-2">
                  <MailIcon className="h-4 w-4" />
                  {user?.email}
                </p>
              </div>
              <Separator />
              <div>
                <label className="text-sm font-medium text-muted-foreground">User ID</label>
                <p className="text-xs font-mono mt-1 text-muted-foreground break-all">{user?.id}</p>
              </div>
            </CardContent>
          </Card>

          {/* Account Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldCheckIcon className="h-5 w-5" />
                Account Status
              </CardTitle>
              <CardDescription>Your account verification and permissions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <label className="text-sm font-medium">Account Status</label>
                  <p className="text-sm text-muted-foreground">Current account state</p>
                </div>
                <Badge variant={user?.is_active ? "default" : "secondary"}>
                  {user?.is_active ? "Active" : "Inactive"}
                </Badge>
              </div>
              <Separator />
              <div className="flex justify-between items-center">
                <div>
                  <label className="text-sm font-medium">Email Verification</label>
                  <p className="text-sm text-muted-foreground">Verify your email address</p>
                </div>
                <Badge variant={user?.is_verified ? "default" : "outline"}>
                  {user?.is_verified ? "Verified" : "Not Verified"}
                </Badge>
              </div>
              <Separator />
              <div className="flex justify-between items-center">
                <div>
                  <label className="text-sm font-medium">Superuser Access</label>
                  <p className="text-sm text-muted-foreground">Administrative privileges</p>
                </div>
                <Badge variant={user?.is_superuser ? "destructive" : "outline"}>
                  {user?.is_superuser ? "Granted" : "Not Granted"}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Activity & Statistics */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CalendarIcon className="h-5 w-5" />
              Activity & Statistics
            </CardTitle>
            <CardDescription>Your account activity and usage statistics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <p className="text-2xl font-bold">0</p>
                <p className="text-sm text-muted-foreground mt-1">Total Orders</p>
              </div>
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <p className="text-2xl font-bold">0</p>
                <p className="text-sm text-muted-foreground mt-1">Wishlist Items</p>
              </div>
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <p className="text-2xl font-bold">0</p>
                <p className="text-sm text-muted-foreground mt-1">Reviews</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Account Actions */}
        <Card className="mt-6 border-destructive/50">
          <CardHeader>
            <CardTitle className="text-destructive">Danger Zone</CardTitle>
            <CardDescription>Irreversible account actions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-medium">Delete Account</p>
                  <p className="text-sm text-muted-foreground">Permanently delete your account and all data</p>
                </div>
                <Button variant="destructive" size="sm">
                  Delete Account
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Dialogs */}
      <EditProfileDialog
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        user={user}
        onSuccess={refreshUser}
      />
      <ChangePasswordDialog
        open={passwordDialogOpen}
        onOpenChange={setPasswordDialogOpen}
        onSuccess={refreshUser}
      />
      <AvatarUploadDialog
        open={avatarDialogOpen}
        onOpenChange={setAvatarDialogOpen}
        currentAvatarUrl={user?.avatar_url || null}
        username={user?.username || "User"}
        onSuccess={refreshUser}
      />
    </div>
  );
}

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <ProfileContent />
    </ProtectedRoute>
  );
}
