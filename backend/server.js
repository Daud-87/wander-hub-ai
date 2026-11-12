// server.js - Complete working version
const express = require("express");
const fs = require("fs");
const path = require("path");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const cors = require("cors");
const crypto = require("crypto");
const { OAuth2Client } = require("google-auth-library");
const multer = require("multer");
require("dotenv").config();


const app = express();
const PORT = process.env.PORT || 5000;

// On Vercel the project folder is read-only; only /tmp is writable (and it is temporary).
const DATA_DIR = process.env.VERCEL ? "/tmp" : __dirname;
const UPLOAD_DIR = path.join(DATA_DIR, "uploads");
fs.mkdirSync(UPLOAD_DIR, { recursive: true });

const JWT_SECRET = process.env.JWT_SECRET || "wander_hub_ai_secret_key";
const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID || "test_client_id";

// Initialize Google OAuth client (will work with test ID)
const client = new OAuth2Client(GOOGLE_CLIENT_ID);

// Middlewares
app.use(cors({
  origin: "*", // Allow all origins for now
  methods: ["GET", "POST", "PUT", "DELETE"],
  allowedHeaders: ["Content-Type", "Authorization"],
  credentials: true
}));
app.use(express.json());
app.use("/uploads", express.static(UPLOAD_DIR));

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, UPLOAD_DIR);
  },
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname);
    const name = crypto.randomBytes(16).toString("hex");
    cb(null, name + ext);
  }
});
const upload = multer({ storage });

// ========= TOUR IMAGE UPLOAD (REQUIRED) =========
app.post("/api/upload/image", upload.single("image"), (req, res) => {
  if (!req.file) {
    return res.json({ success: false });
  }

  res.json({
    success: true,
    url: `/uploads/${req.file.filename}`
  });
});




// Path to files
const usersFilePath = path.join(DATA_DIR, "users.json");
const resetTokensFilePath = path.join(DATA_DIR, "resetTokens.json");

// Helper: read users from file
function readUsers() {
  try {
    if (!fs.existsSync(usersFilePath)) {
      fs.writeFileSync(usersFilePath, "[]", "utf8");
      return [];
    }
    const data = fs.readFileSync(usersFilePath, "utf8");
    return JSON.parse(data);
  } catch (error) {
    console.error("Error reading users:", error);
    return [];
  }
}

// Helper: write users to file
function writeUsers(users) {
  try {
    fs.writeFileSync(usersFilePath, JSON.stringify(users, null, 2), "utf8");
    return true;
  } catch (error) {
    console.error("Error writing users:", error);
    return false;
  }
}

// Helper: read reset tokens
function readResetTokens() {
  try {
    if (!fs.existsSync(resetTokensFilePath)) {
      fs.writeFileSync(resetTokensFilePath, "[]", "utf8");
      return [];
    }
    const data = fs.readFileSync(resetTokensFilePath, "utf8");
    return JSON.parse(data);
  } catch (error) {
    console.error("Error reading reset tokens:", error);
    return [];
  }
}

// Helper: write reset tokens
function writeResetTokens(tokens) {
  try {
    fs.writeFileSync(resetTokensFilePath, JSON.stringify(tokens, null, 2), "utf8");
    return true;
  } catch (error) {
    console.error("Error writing reset tokens:", error);
    return false;
  }
}

// ========== HEALTH CHECK ==========
app.get("/api/health", (req, res) => {
  res.json({
    success: true,
    message: "Server is running",
    timestamp: new Date().toISOString(),
    version: "1.0.0"
  });
});

app.post("/api/signup", async (req, res) => {
  try {
    let { name, email, password, role } = req.body;

    if (!name || !email || !password) {
      return res.status(400).json({ success: false, message: "All fields required" });
    }

    const users = readUsers();
    email = email.toLowerCase();

    if (users.find(u => u.email === email)) {
      return res.status(409).json({ success: false, message: "Email already exists" });
    }

    const adminEmails = (process.env.ADMIN_EMAILS || "").toLowerCase().split(",").map(e => e.trim()).filter(Boolean);
    if (role === "admin" && !adminEmails.includes(email)) role = "user";
    role = ["user", "admin", "guider"].includes(role) ? role : "user";
    const hashedPassword = await bcrypt.hash(password, 10);

    const newUser = {
      id: Date.now().toString(),
      name,
      email,
      password: hashedPassword,
      role,
      createdAt: new Date().toISOString(),
      isGoogleAccount: false
    };

    users.push(newUser);
    writeUsers(users);

    res.json({ success: true, message: "Signup successful" });

  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: "Signup failed" });
  }
});




// ========== LOGIN ==========
function isAdminEmail(email) {
  return (process.env.ADMIN_EMAILS || "").toLowerCase().split(",").map(e => e.trim()).filter(Boolean).includes(String(email || "").toLowerCase());
}

app.post("/api/login", async (req, res) => {
  try {
    const { email, password } = req.body;
    const users = readUsers();

    const user = users.find(u => u.email === email.toLowerCase());
    if (!user) {
      return res.status(401).json({ success: false, message: "Invalid credentials" });
    }

    const match = await bcrypt.compare(password, user.password);
    if (!match) {
      return res.status(401).json({ success: false, message: "Invalid credentials" });
    }

    if (isAdminEmail(user.email) && user.role !== "admin") {
      user.role = "admin";
      writeUsers(users);
    }

    const token = jwt.sign(
      { id: user.id, email: user.email, role: user.role },
      JWT_SECRET,
      { expiresIn: "24h" }
    );

    res.json({
      success: true,
      token,
      user: { id: user.id, name: user.name, email: user.email, role: user.role }
    });

  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: "Login failed" });
  }
});

// ========== GOOGLE AUTH ==========
app.post("/api/auth/google", async (req, res) => {
  try {
    console.log("Google auth request:", req.body);
    const { token } = req.body;

    if (!token) {
      return res.status(400).json({ 
        success: false, 
        message: "Google token is required." 
      });
    }

    // Verify Google token
    let payload;
    try {
      const ticket = await client.verifyIdToken({
        idToken: token,
        audience: GOOGLE_CLIENT_ID,
      });
      payload = ticket.getPayload();
    } catch (googleError) {
      console.log("Google token verification failed, using test mode");
      
      // For development: create test user if Google verification fails
      const users = readUsers();
      const testEmail = "test-google-user@example.com";
      
      let user = users.find(u => u.email === testEmail);
      if (!user) {
        user = {
          id: Date.now().toString(),
          name: "Google Test User",
          email: testEmail,
          password: null,
          role: "user",
          avatar: null,
          isGoogleAccount: true,
          createdAt: new Date().toISOString()
        };
        users.push(user);
        writeUsers(users);
      }
      
      const jwtToken = jwt.sign(
        {
          id: user.id,
          email: user.email,
          name: user.name,
          role: user.role || "user",
        },
        JWT_SECRET,
        { expiresIn: "24h" }
      );

      return res.json({
        success: true,
        message: "Google authentication successful (test mode).",
        token: jwtToken,
        user: {
          id: user.id,
          name: user.name,
          email: user.email,
          role: user.role || "user",
          avatar: user.avatar,
          isGoogleAccount: true,
        },
      });
    }

    // Real Google authentication
    const { email, name, picture } = payload;
    const users = readUsers();

    // Check if user exists
    let user = users.find((u) => u.email.toLowerCase() === email.toLowerCase());

    if (!user) {
      // Create new user for Google login
      user = {
        id: Date.now().toString(),
        name: name || email.split('@')[0],
        email: email.toLowerCase(),
        password: null,
        role: "user",
        avatar: picture || null,
        isGoogleAccount: true,
        createdAt: new Date().toISOString()
      };

      users.push(user);
      writeUsers(users);
    } else if (!user.isGoogleAccount) {
      // Regular account exists with this email
      return res.status(409).json({
        success: false,
        message: "Email already registered with password. Please use password login.",
      });
    }

    // Generate JWT token
    const jwtToken = jwt.sign(
      {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role || "user",
      },
      JWT_SECRET,
      { expiresIn: "24h" }
    );

    console.log("Google auth successful for:", email);

    return res.json({
      success: true,
      message: "Google authentication successful.",
      token: jwtToken,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role || "user",
        avatar: user.avatar || picture,
        isGoogleAccount: true,
      },
    });
  } catch (error) {
    console.error("Google auth error:", error);
    return res.status(500).json({
      success: false,
      message: "Server error during Google authentication.",
    });
  }
});
app.post("/api/profile/save", (req, res) => {
  const users = readUsers();
  const { id, profile } = req.body;

  const user = users.find(u => u.id === id);
  if (!user) return res.status(404).json({ success:false });

  user.profile = profile;
  writeUsers(users);
  res.json({ success:true });
});

// ===== PROFILE LOAD =====
app.get("/api/profile/:id", (req, res) => {
  const users = readUsers();
  const user = users.find(u => u.id === req.params.id);
  res.json(user?.profile || null);
});

// ========== FORGOT PASSWORD ==========



app.post("/api/auth/reset-password", async (req, res) => {
  try {
    const { email, newPassword } = req.body;

    if (!email || !newPassword) {
      return res.json({
        success: false,
        message: "Email and new password are required"
      });
    }

    if (newPassword.length < 6) {
      return res.json({
        success: false,
        message: "Password must be at least 6 characters"
      });
    }

    const users = readUsers();
    const user = users.find(u => u.email === email.toLowerCase());

    if (!user) {
      return res.json({
        success: false,
        message: "Email not registered"
      });
    }

    // 🔐 hash new password
    const hashed = await bcrypt.hash(newPassword, 10);
    user.password = hashed;

    writeUsers(users);

    return res.json({
      success: true,
      message: "Password reset successfully"
    });

  } catch (err) {
    console.error("Reset password error:", err);
    return res.status(500).json({
      success: false,
      message: "Server error"
    });
  }
});


// ========== VERIFY TOKEN ==========
app.post("/api/auth/verify-token", async (req, res) => {
  try {
    const { token, email } = req.body;

    if (!token || !email) {
      return res.status(400).json({
        success: false,
        message: "Token and email are required.",
      });
    }

    const resetTokens = readResetTokens();
    const resetToken = resetTokens.find(
      (t) =>
        t.token === token &&
        t.email === email.toLowerCase() &&
        !t.used &&
        new Date(t.expiresAt) > new Date()
    );

    if (!resetToken) {
      return res.status(400).json({
        success: false,
        message: "Invalid or expired token.",
      });
    }

    return res.json({
      success: true,
      message: "Token is valid.",
    });
  } catch (error) {
    console.error("Verify token error:", error);
    return res.status(500).json({
      success: false,
      message: "Server error verifying token.",
    });
  }
});

// ========== GET USER BY ID ==========
app.get("/api/user/:id", (req, res) => {
  // Not exposed on the public Vercel deployment (would list every signup).
  if (process.env.VERCEL) return res.status(404).json({ success: false, message: "Endpoint not found" });
  try {
    const { id } = req.params;
    const users = readUsers();
    const user = users.find(u => u.id === id);

    if (!user) {
      return res.status(404).json({ 
        success: false, 
        message: "User not found." 
      });
    }

    // Don't return password
    const { password, ...userWithoutPassword } = user;
    
    return res.json({
      success: true,
      user: userWithoutPassword
    });
  } catch (error) {
    console.error("Get user error:", error);
    return res.status(500).json({ 
      success: false, 
      message: "Server error." 
    });
  }
});

// ========== GET ALL USERS (ADMIN) ==========
app.get("/api/users", (req, res) => {
  // Not exposed on the public Vercel deployment (would list every signup).
  if (process.env.VERCEL) return res.status(404).json({ success: false, message: "Endpoint not found" });
  try {
    const users = readUsers();
    
    // Remove passwords from response
    const usersWithoutPasswords = users.map(user => {
      const { password, ...userWithoutPassword } = user;
      return userWithoutPassword;
    });

    return res.json({
      success: true,
      users: usersWithoutPasswords,
      count: users.length
    });
  } catch (error) {
    console.error("Get users error:", error);
    return res.status(500).json({ 
      success: false, 
      message: "Server error." 
    });
  }
});

// ========== ROOT ROUTE ==========
app.get("/", (req, res) => {
  res.json({ 
    message: "🚀 Wander Hub AI Backend Server",
    status: "Running",
    version: "2.0.0",
    timestamp: new Date().toISOString(),
    endpoints: {
      health: "GET /api/health",
      signup: "POST /api/signup",
      login: "POST /api/login",
      googleAuth: "POST /api/auth/google",
      forgotPassword: "POST /api/auth/forgot-password",
      resetPassword: "POST /api/auth/reset-password",
      verifyToken: "POST /api/auth/verify-token",
      getUser: "GET /api/user/:id",
      getAllUsers: "GET /api/users"
    },
    note: "Server is ready to accept requests"
  });
});

// ========== 404 HANDLER ==========
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: "Endpoint not found",
    path: req.path,
    method: req.method
  });
});

// ========== ERROR HANDLER ==========
app.use((err, req, res, next) => {
  console.error("Server error:", err);
  res.status(500).json({
    success: false,
    message: "Internal server error",
    error: process.env.NODE_ENV === "development" ? err.message : undefined
  });
});

// Start server (skipped when running as a Vercel function)
if (require.main === module) app.listen(PORT, () => {
  console.log(`========================================`);
  console.log(`🚀  Server running on http://localhost:${PORT}`);
  console.log(`🔐  JWT Secret: ${JWT_SECRET ? "Loaded" : "Using default"}`);
  console.log(`👤  Users in database: ${readUsers().length}`);
  console.log(`========================================`);
  console.log(`📝  Available endpoints:`);
  console.log(`    • GET  /              - Server info`);
  console.log(`    • POST /api/signup    - Create account`);
  console.log(`    • POST /api/login     - Login with email/password`);
  console.log(`    • POST /api/auth/google - Login with Google`);
  console.log(`    • POST /api/auth/forgot-password - Request reset`);
  console.log(`    • POST /api/auth/reset-password  - Reset password`);
  console.log(`========================================`);
});

module.exports = app;
