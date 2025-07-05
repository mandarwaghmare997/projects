# Qryti Learn Production Deployment Checklist

## Pre-Deployment
- [ ] SSL certificates obtained and configured
- [ ] Domain DNS configured (learn.qryti.com, api.qryti.com)
- [ ] Server provisioned with adequate resources (2+ CPU, 4GB+ RAM)
- [ ] Firewall configured (ports 80, 443, 22)
- [ ] Backup storage configured
- [ ] Monitoring tools installed (optional: Prometheus, Grafana)

## Environment Configuration
- [ ] Update .env.production files with actual values
- [ ] Set secure SECRET_KEY and JWT_SECRET_KEY
- [ ] Configure email settings for notifications
- [ ] Set up database connection (PostgreSQL recommended for production)
- [ ] Configure file storage (AWS S3 recommended)

## Security Configuration
- [ ] Change default passwords and keys
- [ ] Configure rate limiting
- [ ] Set up SSL/TLS certificates
- [ ] Configure security headers
- [ ] Set up fail2ban for SSH protection
- [ ] Configure database access restrictions

## Application Deployment
- [ ] Build frontend for production (npm run build)
- [ ] Run database migrations
- [ ] Copy application files to production server
- [ ] Install and configure systemd services
- [ ] Configure Nginx reverse proxy
- [ ] Set up log rotation

## Testing
- [ ] Verify API endpoints are accessible
- [ ] Test user registration and login
- [ ] Verify certificate generation
- [ ] Test file uploads and downloads
- [ ] Check SSL certificate validity
- [ ] Verify monitoring endpoints

## Monitoring Setup
- [ ] Configure log aggregation
- [ ] Set up health check monitoring
- [ ] Configure alerting for critical issues
- [ ] Set up performance monitoring
- [ ] Configure backup monitoring

## Post-Deployment
- [ ] Verify all services are running
- [ ] Test complete user workflow
- [ ] Set up automated backups
- [ ] Configure monitoring alerts
- [ ] Document any custom configurations
- [ ] Train support team on monitoring tools

## Maintenance
- [ ] Schedule regular security updates
- [ ] Set up automated backup verification
- [ ] Plan capacity monitoring and scaling
- [ ] Document incident response procedures
- [ ] Set up log analysis and alerting
