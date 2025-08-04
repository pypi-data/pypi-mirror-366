"""
LazyPip Theme Configuration
===========================

This module contains the CSS styling for the LazyPip TUI application.
It defines colors, layouts, and styling for all widgets and screens.
"""

LAZYPIP_CSS = """
/* === GLOBAL STYLES === */
Screen {
    background: $background;
    color: $text;
}

/* === COLOR VARIABLES === */
App {
    /* Dark theme colors */
    background: #1a1a1a;
    surface: #2d2d2d;
    primary: #61dafb;
    secondary: #bb86fc;
    accent: #03dac6;
    warning: #ffb74d;
    error: #f44336;
    success: #4caf50;

    text: #ffffff;
    text-muted: #a0a0a0;
    text-disabled: #666666;

    border: #444444;
    border-accent: #61dafb;
}

/* === LAYOUT COMPONENTS === */
Header {
    background: $primary;
    color: $background;
    text-style: bold;
    padding: 0 1;
}

Footer {
    background: $surface;
    color: $text;
    border-top: solid $border;
    padding: 0 1;
}

/* === MAIN SCREEN === */
MainScreen {
    layout: grid;
    grid-size: 2;
    grid-columns: 1fr 1fr;
    grid-rows: 1fr;
}

.left-panel {
    border: solid $border;
    margin: 0 1 0 0;
    background: $surface;
}

.right-panel {
    border: solid $border;
    margin: 0 0 0 1;
    background: $surface;
}

.focused {
    border: solid $accent;
    border-title-color: $accent;
}

/* === PACKAGE LIST === */
PackageList {
    padding: 1;
}

PackageList DataTable {
    background: $surface;
    color: $text;
}

PackageList DataTable > .datatable--header {
    background: $primary;
    color: $background;
    text-style: bold;
}

PackageList DataTable > .datatable--cursor {
    background: $accent 30%;
    color: $text;
}

PackageList DataTable > .datatable--hover {
    background: $primary 20%;
}

/* Package status styling */
.package-installed {
    color: $success;
}

.package-outdated {
    color: $warning;
}

.package-not-installed {
    color: $error;
}

.package-unknown {
    color: $text-muted;
}

/* === PACKAGE DETAILS === */
PackageDetails {
    padding: 1;
    background: $surface;
}

.package-header {
    background: $primary;
    color: $background;
    text-style: bold;
    padding: 1;
    margin-bottom: 1;
}

.package-info {
    padding: 1;
    color: $text;
}

.no-selection {
    text-align: center;
    color: $text-muted;
    padding: 3;
    text-style: italic;
}

.package-name {
    text-style: bold;
    color: $accent;
}

.package-version {
    color: $text;
}

.package-latest {
    color: $warning;
    text-style: bold;
}

.package-summary {
    color: $text-muted;
    margin: 1 0;
}

.package-location {
    color: $text-disabled;
    text-style: italic;
}

.dependency-list {
    color: $text;
    margin: 1 0;
}

.status-indicator {
    text-style: bold;
}

.status-installed {
    color: $success;
}

.status-outdated {
    color: $warning;
}

.status-not-installed {
    color: $error;
}

/* === STATUS BAR === */
StatusBar {
    dock: bottom;
    height: 3;
    background: $surface;
    border-top: solid $border;
}

.status-content {
    padding: 0 1;
    height: 3;
    layout: grid;
    grid-size: 2;
    grid-columns: 1fr 1fr;
}

.status-message {
    color: $text;
    text-align: left;
    content-align: center left;
}

.shortcuts {
    color: $text-muted;
    text-align: right;
    content-align: center right;
}

/* === TABBED CONTENT === */
TabbedContent {
    background: $surface;
}

TabbedContent > ContentTabs {
    background: $background;
    color: $text;
}

TabbedContent > ContentTabs > Tab {
    background: $surface;
    color: $text-muted;
    border: solid $border;
    margin: 0 1 0 0;
    padding: 0 2;
}

TabbedContent > ContentTabs > Tab.-active {
    background: $primary;
    color: $background;
    text-style: bold;
}

TabbedContent > ContentTabs > Tab:hover {
    background: $primary 50%;
    color: $text;
}

/* === MODAL DIALOGS === */
ModalScreen {
    align: center middle;
    background: rgba(0, 0, 0, 0.8);
}

/* Install Dialog */
InstallDialog > #dialog {
    width: 60;
    height: 15;
    border: thick $primary;
    background: $surface;
    padding: 1 2;
}

InstallDialog #title {
    color: $primary;
    text-align: center;
    text-style: bold;
    margin-bottom: 1;
}

InstallDialog #package-input {
    margin: 1 0;
    border: solid $border;
    background: $background;
    color: $text;
}

InstallDialog #package-input:focus {
    border: solid $accent;
}

InstallDialog #buttons {
    align: center middle;
    margin-top: 1;
}

InstallDialog Button {
    margin: 0 1;
    min-width: 10;
}

/* Confirmation Dialog */
ConfirmationDialog > #dialog {
    width: 50;
    height: 12;
    border: thick $warning;
    background: $surface;
    padding: 1 2;
}

ConfirmationDialog #title {
    color: $warning;
    text-align: center;
    text-style: bold;
    margin-bottom: 1;
}

ConfirmationDialog #message {
    text-align: center;
    margin: 1 0;
    color: $text;
    text-style: bold;
}

ConfirmationDialog #buttons {
    align: center middle;
    margin-top: 2;
}

ConfirmationDialog Button {
    margin: 0 1;
    min-width: 8;
}

/* === BUTTONS === */
Button {
    background: $surface;
    color: $text;
    border: solid $border;
    padding: 0 2;
    text-style: bold;
}

Button:hover {
    background: $primary;
    color: $background;
    border: solid $primary;
}

Button:focus {
    background: $accent;
    color: $background;
    border: solid $accent;
}

Button.-primary {
    background: $primary;
    color: $background;
    border: solid $primary;
}

Button.-primary:hover {
    background: $accent;
    border: solid $accent;
}

Button.-error {
    background: $error;
    color: $text;
    border: solid $error;
}

Button.-error:hover {
    background: $error 80%;
    border: solid $error;
}

Button.-warning {
    background: $warning;
    color: $background;
    border: solid $warning;
}

Button.-warning:hover {
    background: $warning 80%;
    border: solid $warning;
}

/* === INPUT FIELDS === */
Input {
    background: $background;
    color: $text;
    border: solid $border;
    padding: 0 1;
}

Input:focus {
    border: solid $accent;
    background: $surface;
}

Input > .input--placeholder {
    color: $text-disabled;
    text-style: italic;
}

/* === LABELS AND STATIC TEXT === */
Label {
    color: $text;
}

Static {
    color: $text;
}

.hint {
    color: $text-muted;
    text-align: center;
    margin: 1 0;
    text-style: italic;
}

.error-text {
    color: $error;
    text-style: bold;
}

.success-text {
    color: $success;
    text-style: bold;
}

.warning-text {
    color: $warning;
    text-style: bold;
}

/* === CONTAINERS === */
Vertical {
    background: transparent;
}

Horizontal {
    background: transparent;
}

Container {
    background: transparent;
}

/* === SCROLLBARS === */
ScrollBar {
    background: $surface;
    color: $border;
}

ScrollBar:hover {
    background: $primary 20%;
}

/* === LOADING STATES === */
.loading {
    text-align: center;
    color: $text-muted;
    text-style: italic;
}

.loading-spinner {
    color: $accent;
    text-style: bold;
}

/* === PROGRESS BARS === */
ProgressBar {
    background: $surface;
    color: $accent;
    border: solid $border;
}

ProgressBar > .bar--bar {
    background: $accent;
}

ProgressBar > .bar--complete {
    background: $success;
}

/* === NOTIFICATIONS === */
.notification {
    background: $surface;
    border: solid $accent;
    padding: 1;
    margin: 1;
}

.notification-success {
    border: solid $success;
    color: $success;
}

.notification-error {
    border: solid $error;
    color: $error;
}

.notification-warning {
    border: solid $warning;
    color: $warning;
}

/* === RESPONSIVE ADJUSTMENTS === */
/* For smaller screens */
@media (max-width: 80) {
    MainScreen {
        grid-columns: 1fr;
        grid-rows: 1fr 1fr;
    }

    .left-panel {
        margin: 0 0 1 0;
    }

    .right-panel {
        margin: 1 0 0 0;
    }
}

/* === KEYBOARD SHORTCUT INDICATORS === */
.shortcut-key {
    color: $accent;
    text-style: bold;
    background: $surface;
    padding: 0 1;
    border: solid $border;
}

.shortcut-desc {
    color: $text-muted;
    margin-left: 1;
}

/* === FOCUS INDICATORS === */
*:focus {
    border: solid $accent;
}

*:focus-within {
    border-color: $accent 50%;
}

/* === SELECTION STYLES === */
.selected {
    background: $accent 30%;
    color: $text;
    text-style: bold;
}

.highlighted {
    background: $primary 20%;
    color: $text;
}
"""

LIGHT_THEME_CSS = """
App {
    /* Light theme colors */
    background: #ffffff;
    surface: #f5f5f5;
    primary: #1976d2;
    secondary: #7b1fa2;
    accent: #00796b;
    warning: #f57c00;
    error: #d32f2f;
    success: #388e3c;

    text: #212121;
    text-muted: #757575;
    text-disabled: #bdbdbd;

    border: #e0e0e0;
    border-accent: #1976d2;
}
"""

HIGH_CONTRAST_CSS = """
App {
    /* High contrast theme colors */
    background: #000000;
    surface: #1a1a1a;
    primary: #ffffff;
    secondary: #ffff00;
    accent: #00ffff;
    warning: #ffaa00;
    error: #ff0000;
    success: #00ff00;

    text: #ffffff;
    text-muted: #cccccc;
    text-disabled: #666666;

    border: #ffffff;
    border-accent: #00ffff;
}
"""
