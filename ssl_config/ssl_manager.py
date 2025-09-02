"""
SSL/TLS certificate management and configuration
"""

import os
import subprocess
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import OpenSSL
from OpenSSL import crypto
import hashlib

class SSLManager:
    """
    SSL/TLS certificate management and configuration
    """

    def __init__(self, cert_dir: str = "./ssl"):
        """
        Initialize SSL manager

        Args:
            cert_dir: Directory to store SSL certificates
        """
        self.cert_dir = cert_dir
        self.cert_file = os.path.join(cert_dir, "server.crt")
        self.key_file = os.path.join(cert_dir, "server.key")
        self.ca_file = os.path.join(cert_dir, "ca.crt")

        # Create certificate directory if it doesn't exist
        os.makedirs(cert_dir, exist_ok=True)

    def generate_self_signed_cert(self, domain: str = "localhost",
                                validity_days: int = 365,
                                key_size: int = 2048) -> Tuple[str, str]:
        """
        Generate self-signed SSL certificate

        Args:
            domain: Domain name for the certificate
            validity_days: Certificate validity period in days
            key_size: RSA key size

        Returns:
            Tuple of (certificate_path, key_path)
        """
        # Generate key
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, key_size)

        # Generate certificate
        cert = crypto.X509()
        cert.get_subject().C = "US"
        cert.get_subject().ST = "California"
        cert.get_subject().L = "San Francisco"
        cert.get_subject().O = "Owlban Group"
        cert.get_subject().OU = "IT Department"
        cert.get_subject().CN = domain

        cert.get_issuer().C = "US"
        cert.get_issuer().ST = "California"
        cert.get_issuer().L = "San Francisco"
        cert.get_issuer().O = "Owlban Group"
        cert.get_issuer().OU = "IT Department"
        cert.get_issuer().CN = domain

        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(validity_days * 24 * 60 * 60)
        cert.set_pubkey(key)
        cert.sign(key, 'sha256')

        # Save certificate and key
        with open(self.cert_file, 'wb') as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

        with open(self.key_file, 'wb') as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

        print(f"✅ Self-signed certificate generated for {domain}")
        print(f"   Certificate: {self.cert_file}")
        print(f"   Private key: {self.key_file}")

        return self.cert_file, self.key_file

    def generate_ca_signed_cert(self, domain: str, ca_cert_path: str,
                              ca_key_path: str, validity_days: int = 365,
                              key_size: int = 2048) -> Tuple[str, str]:
        """
        Generate CA-signed SSL certificate

        Args:
            domain: Domain name for the certificate
            ca_cert_path: Path to CA certificate
            ca_key_path: Path to CA private key
            validity_days: Certificate validity period in days
            key_size: RSA key size

        Returns:
            Tuple of (certificate_path, key_path)
        """
        # Load CA certificate and key
        with open(ca_cert_path, 'rb') as f:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())

        with open(ca_key_path, 'rb') as f:
            ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())

        # Generate server key
        server_key = crypto.PKey()
        server_key.generate_key(crypto.TYPE_RSA, key_size)

        # Generate server certificate
        server_cert = crypto.X509()
        server_cert.get_subject().C = "US"
        server_cert.get_subject().ST = "California"
        server_cert.get_subject().L = "San Francisco"
        server_cert.get_subject().O = "Owlban Group"
        server_cert.get_subject().OU = "IT Department"
        server_cert.get_subject().CN = domain

        server_cert.get_issuer().C = ca_cert.get_subject().C
        server_cert.get_issuer().ST = ca_cert.get_subject().ST
        server_cert.get_issuer().L = ca_cert.get_subject().L
        server_cert.get_issuer().O = ca_cert.get_subject().O
        server_cert.get_issuer().OU = ca_cert.get_subject().OU
        server_cert.get_issuer().CN = ca_cert.get_subject().CN

        server_cert.set_serial_number(1001)
        server_cert.gmtime_adj_notBefore(0)
        server_cert.gmtime_adj_notAfter(validity_days * 24 * 60 * 60)
        server_cert.set_pubkey(server_key)
        server_cert.sign(ca_key, 'sha256')

        # Save server certificate and key
        with open(self.cert_file, 'wb') as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, server_cert))

        with open(self.key_file, 'wb') as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, server_key))

        print(f"✅ CA-signed certificate generated for {domain}")
        print(f"   Certificate: {self.cert_file}")
        print(f"   Private key: {self.key_file}")

        return self.cert_file, self.key_file

    def get_cert_info(self, cert_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get certificate information

        Args:
            cert_path: Path to certificate file (uses self.cert_file if None)

        Returns:
            Dictionary with certificate information
        """
        cert_file = cert_path or self.cert_file

        if not os.path.exists(cert_file):
            return {'error': 'Certificate file not found'}

        try:
            with open(cert_file, 'rb') as f:
                cert_data = f.read()

            cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)

            # Extract certificate information
            subject = cert.get_subject()
            issuer = cert.get_issuer()

            info = {
                'subject': {
                    'country': subject.C,
                    'state': subject.ST,
                    'locality': subject.L,
                    'organization': subject.O,
                    'organizational_unit': subject.OU,
                    'common_name': subject.CN
                },
                'issuer': {
                    'country': issuer.C,
                    'state': issuer.ST,
                    'locality': issuer.L,
                    'organization': issuer.O,
                    'organizational_unit': issuer.OU,
                    'common_name': issuer.CN
                },
                'serial_number': str(cert.get_serial_number()),
                'not_before': datetime.strptime(
                    cert.get_notBefore().decode('ascii'),
                    '%Y%m%d%H%M%SZ'
                ).isoformat(),
                'not_after': datetime.strptime(
                    cert.get_notAfter().decode('ascii'),
                    '%Y%m%d%H%M%SZ'
                ).isoformat(),
                'signature_algorithm': cert.get_signature_algorithm().decode('ascii'),
                'version': cert.get_version(),
                'fingerprint_sha256': cert.digest('sha256').decode('ascii'),
                'fingerprint_sha1': cert.digest('sha1').decode('ascii')
            }

            # Check if certificate is expired
            not_after = datetime.strptime(
                cert.get_notAfter().decode('ascii'),
                '%Y%m%d%H%M%SZ'
            )
            info['is_expired'] = datetime.now() > not_after
            info['days_until_expiry'] = (not_after - datetime.now()).days

            return info

        except Exception as e:
            return {'error': f'Failed to read certificate: {str(e)}'}

    def check_cert_validity(self, cert_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Check certificate validity and expiration

        Args:
            cert_path: Path to certificate file (uses self.cert_file if None)

        Returns:
            Dictionary with validity information
        """
        info = self.get_cert_info(cert_path)

        if 'error' in info:
            return info

        validity = {
            'is_valid': not info.get('is_expired', True),
            'is_expired': info.get('is_expired', True),
            'days_until_expiry': info.get('days_until_expiry', 0),
            'expires_at': info.get('not_after'),
            'issued_at': info.get('not_before')
        }

        # Add warning for certificates expiring soon
        if validity['days_until_expiry'] <= 30 and not validity['is_expired']:
            validity['warning'] = f"Certificate expires in {validity['days_until_expiry']} days"

        return validity

    def generate_dh_params(self, dh_file: str = "dhparam.pem", key_size: int = 2048):
        """
        Generate Diffie-Hellman parameters for perfect forward secrecy

        Args:
            dh_file: Output file for DH parameters
            key_size: DH key size
        """
        dh_path = os.path.join(self.cert_dir, dh_file)

        try:
            # Generate DH parameters using OpenSSL command
            cmd = ['openssl', 'dhparam', '-out', dh_path, str(key_size)]
            subprocess.run(cmd, check=True, capture_output=True)

            print(f"✅ DH parameters generated: {dh_path}")
            return dh_path

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate DH parameters: {e}")
            return None

    def setup_ssl_context(self, cert_path: Optional[str] = None,
                         key_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Setup SSL context configuration for web servers

        Args:
            cert_path: Path to SSL certificate
            key_path: Path to SSL private key

        Returns:
            Dictionary with SSL context configuration
        """
        cert_file = cert_path or self.cert_file
        key_file = key_path or self.key_file

        if not os.path.exists(cert_file) or not os.path.exists(key_file):
            return {'error': 'Certificate or key file not found'}

        # Generate DH parameters if they don't exist
        dh_file = os.path.join(self.cert_dir, "dhparam.pem")
        if not os.path.exists(dh_file):
            self.generate_dh_params()

        ssl_config = {
            'cert_file': cert_file,
            'key_file': key_file,
            'dh_file': dh_file if os.path.exists(dh_file) else None,
            'protocols': ['TLSv1.2', 'TLSv1.3'],
            'ciphers': [
                'ECDHE-RSA-AES128-GCM-SHA256',
                'ECDHE-RSA-AES256-GCM-SHA384',
                'ECDHE-RSA-CHACHA20-POLY1305'
            ],
            'hsts_max_age': 31536000,  # 1 year
            'session_cache_timeout': 300,  # 5 minutes
            'ocsp_stapling': True,
            'strict_transport_security': True
        }

        return ssl_config

    def create_ssl_config_file(self, output_path: str = "ssl_config.json") -> str:
        """
        Create SSL configuration file

        Args:
            output_path: Path to save SSL configuration

        Returns:
            Path to created configuration file
        """
        config_path = os.path.join(self.cert_dir, output_path)

        # Generate certificates if they don't exist
        if not os.path.exists(self.cert_file) or not os.path.exists(self.key_file):
            self.generate_self_signed_cert()

        # Get SSL configuration
        ssl_config = self.setup_ssl_context()
        cert_info = self.get_cert_info()

        config = {
            'ssl_enabled': True,
            'certificate_info': cert_info,
            'ssl_context': ssl_config,
            'security_headers': {
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
                'X-Frame-Options': 'DENY',
                'X-Content-Type-Options': 'nosniff',
                'X-XSS-Protection': '1; mode=block',
                'Referrer-Policy': 'strict-origin-when-cross-origin',
                'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
            },
            'generated_at': datetime.now().isoformat()
        }

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ SSL configuration saved to {config_path}")
        return config_path

def generate_ssl_cert(domain: str = "localhost", cert_dir: str = "./ssl",
                     ca_signed: bool = False, ca_cert: Optional[str] = None,
                     ca_key: Optional[str] = None) -> Dict[str, str]:
    """
    Generate SSL certificate (convenience function)

    Args:
        domain: Domain name for the certificate
        cert_dir: Directory to store certificates
        ca_signed: Whether to generate CA-signed certificate
        ca_cert: Path to CA certificate (required if ca_signed=True)
        ca_key: Path to CA private key (required if ca_signed=True)

    Returns:
        Dictionary with certificate paths
    """
    manager = SSLManager(cert_dir)

    if ca_signed and ca_cert and ca_key:
        cert_path, key_path = manager.generate_ca_signed_cert(domain, ca_cert, ca_key)
    else:
        cert_path, key_path = manager.generate_self_signed_cert(domain)

    return {
        'certificate': cert_path,
        'private_key': key_path,
        'ca_certificate': manager.ca_file if ca_signed else None
    }

# Example usage
if __name__ == "__main__":
    # Generate self-signed certificate for development
    certs = generate_ssl_cert("localhost", "./ssl")
    print("Development SSL certificates generated:")
    print(f"Certificate: {certs['certificate']}")
    print(f"Private Key: {certs['private_key']}")

    # Create SSL configuration
    manager = SSLManager("./ssl")
    config_file = manager.create_ssl_config_file()
    print(f"SSL configuration created: {config_file}")
