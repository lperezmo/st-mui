import { LicenseInfo } from "@mui/x-license";

let licenseApplied = false;

/**
 * Apply a MUI X license key (Pro/Premium). Only applies once per session.
 * Without a key, Pro components work in evaluation mode (watermark + console warnings).
 */
export function applyMuiLicense(key: string | null | undefined): void {
  if (key && !licenseApplied) {
    LicenseInfo.setLicenseKey(key);
    licenseApplied = true;
  }
}
