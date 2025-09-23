// Enhanced Safety Dashboard Component
class EnhancedSafetyDashboard extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            // Core data
            sheets: [],
            analyticsData: null,
            loading: true,
            error: null,
            
            // Visualization states
            activeTab: 'executive',
            kpiData: {},
            heatmapData: [],
            trendData: {},
            correlationData: {},
            forecastData: {},
            complianceData: {},
            benchmarkData: {},
            
            // Real-time listeners
            unsubscribeListeners: [],
            
            // Alerting
            alertThresholds: {
                incidentRate: 5,
                complianceRate: 80,
                trainingCompletion: 90
            },
            alerts: []
        };
        
        this.chartsRef = React.createRef();
        this.chartInstances = {};
        this.alertCheckInterval = null;
    }
    
    componentDidMount() {
        this.fetchData();
        this.fetchAnalytics();
        this.setupRealTimeListeners();
        this.startAlertChecking();
    }
    
    componentWillUnmount() {
        // Unsubscribe from all listeners when component unmounts
        this.state.unsubscribeListeners.forEach(unsubscribe => {
            if (typeof unsubscribe === 'function') {
                unsubscribe();
            }
        });
        
        // Clear alert checking interval
        if (this.alertCheckInterval) {
            clearInterval(this.alertCheckInterval);
        }
    }
    
    // Start periodic alert checking
    startAlertChecking() {
        // Check for alerts every 5 minutes
        this.alertCheckInterval = setInterval(() => {
            this.checkForAlerts();
        }, 5 * 60 * 1000); // 5 minutes in milliseconds
    }
    
    // Check for threshold violations and generate alerts
    checkForAlerts() {
        const { kpiData, complianceData, alertThresholds } = this.state;
        const newAlerts = [];
        
        // Check incident rate threshold
        if (kpiData.incidentRate > alertThresholds.incidentRate) {
            newAlerts.push({
                id: Date.now(),
                type: 'warning',
                message: `High incident rate detected: ${kpiData.incidentRate}% (threshold: ${alertThresholds.incidentRate}%)`,
                timestamp: new Date().toISOString()
            });
        }
        
        // Check compliance rate threshold
        if (complianceData.compliance_rate < alertThresholds.complianceRate) {
            newAlerts.push({
                id: Date.now() + 1,
                type: 'warning',
                message: `Low compliance rate detected: ${complianceData.compliance_rate?.toFixed(1)}% (threshold: ${alertThresholds.complianceRate}%)`,
                timestamp: new Date().toISOString()
            });
        }
        
        // Check training completion threshold
        if (complianceData.training_completion_rate < alertThresholds.trainingCompletion) {
            newAlerts.push({
                id: Date.now() + 2,
                type: 'warning',
                message: `Low training completion rate detected: ${complianceData.training_completion_rate?.toFixed(1)}% (threshold: ${alertThresholds.trainingCompletion}%)`,
                timestamp: new Date().toISOString()
            });
        }
        
        // Add new alerts to state if any
        if (newAlerts.length > 0) {
            this.setState(prevState => ({
                alerts: [...newAlerts, ...prevState.alerts].slice(0, 10) // Keep only last 10 alerts
            }));
            
            // Show browser notification if permission granted
            if (Notification.permission === 'granted') {
                newAlerts.forEach(alert => {
                    new Notification('Safety Alert', {
                        body: alert.message,
                        icon: '/favicon.ico'
                    });
                });
            }
        }
    }
    
    // Render alert panel
    renderAlertPanel() {
        const { alerts } = this.state;
        
        if (alerts.length === 0) return null;
        
        return React.createElement('div', {
            style: {
                backgroundColor: '#fffbeb',
                border: '1px solid #fbbf24',
                borderRadius: '0.5rem',
                padding: '1rem',
                marginBottom: '1rem'
            }
        },
            React.createElement('h4', {
                style: {
                    color: '#92400e',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                }
            },
                React.createElement('i', { className: 'bi bi-exclamation-triangle-fill' }),
                'Safety Alerts'
            ),
            React.createElement('ul', {
                style: {
                    listStyle: 'none',
                    padding: 0,
                    margin: 0
                }
            },
                alerts.map(alert => 
                    React.createElement('li', {
                        key: alert.id,
                        style: {
                            padding: '0.5rem',
                            borderBottom: '1px solid #fbbf24',
                            display: 'flex',
                            justifyContent: 'space-between'
                        }
                    },
                        React.createElement('span', null, alert.message),
                        React.createElement('span', {
                            style: {
                                fontSize: '0.8rem',
                                color: '#92400e'
                            }
                        }, new Date(alert.timestamp).toLocaleTimeString())
                    )
                )
            ),
            React.createElement('div', {
                style: {
                    textAlign: 'right',
                    marginTop: '0.5rem'
                }
            },
                React.createElement('button', {
                    className: 'btn',
                    onClick: () => this.setState({ alerts: [] }),
                    style: {
                        backgroundColor: '#f59e0b',
                        color: 'white',
                        fontSize: '0.9rem'
                    }
                }, 'Clear Alerts')
            )
        );
    }
    
    // Set up real-time listeners for Firestore collections
    setupRealTimeListeners() {
        if (!window.db || !isFirebaseInitialized) {
            console.warn('Firebase not initialized, skipping real-time listeners');
            return;
        }
        
        const db = window.db;
        const unsubscribeListeners = [];
        
        // Listen for changes in Incidents collection
        const incidentsUnsubscribe = db.collection('Incidents').onSnapshot((snapshot) => {
            console.log('Incidents collection updated');
            this.fetchData(); // Refresh data when incidents change
        }, (error) => {
            console.error('Error listening to Incidents collection:', error);
        });
        
        // Listen for changes in Inspections collection
        const inspectionsUnsubscribe = db.collection('Inspections').onSnapshot((snapshot) => {
            console.log('Inspections collection updated');
            this.fetchData(); // Refresh data when inspections change
        }, (error) => {
            console.error('Error listening to Inspections collection:', error);
        });
        
        // Listen for changes in Trainings collection
        const trainingsUnsubscribe = db.collection('Trainings').onSnapshot((snapshot) => {
            console.log('Trainings collection updated');
            this.fetchData(); // Refresh data when trainings change
        }, (error) => {
            console.error('Error listening to Trainings collection:', error);
        });
        
        // Store unsubscribe functions
        unsubscribeListeners.push(incidentsUnsubscribe, inspectionsUnsubscribe, trainingsUnsubscribe);
        
        // Update state with unsubscribe functions
        this.setState({ unsubscribeListeners });
    }
    
    // Fetch core Firestore data
    async fetchData() {
        try {
            this.setState({ loading: true });
            
            if (!window.db || !isFirebaseInitialized) {
                throw new Error('Firebase not initialized');
            }
            
            const db = window.db;
            const uploadedCollections = JSON.parse(localStorage.getItem('uploadedCollections') || '[]');
            
            if (uploadedCollections.length === 0) {
                this.setState({ sheets: [], loading: false });
                return;
            }
            
            // Fetch data for each collection
            const sheetsData = [];
            for (const collectionName of uploadedCollections) {
                try {
                    const querySnapshot = await db.collection(collectionName).get();
                    const data = [];
                    querySnapshot.forEach((doc) => {
                        data.push({ id: doc.id, ...doc.data() });
                    });
                    sheetsData.push({ name: collectionName, data });
                } catch (err) {
                    console.error(`Error fetching data for ${collectionName}:`, err);
                }
            }
            
            this.setState({ sheets: sheetsData, loading: false });
            
            // Calculate KPIs
            this.calculateKPIs(sheetsData);
        } catch (err) {
            this.setState({ 
                error: 'Failed to fetch data from Firestore: ' + err.message,
                loading: false 
            });
            console.error('Error fetching data:', err);
        }
    }
    
    // Fetch analytics data from backend
    async fetchAnalytics() {
        try {
            const response = await fetch('http://localhost:5000/api/get-safety-analytics');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.setState({ 
                    analyticsData: result.results,
                    heatmapData: this.processHeatmapData(result.results),
                    trendData: this.processTrendData(result.results),
                    correlationData: this.processCorrelationData(result.results),
                    forecastData: this.processForecastData(result.results),
                    complianceData: this.processComplianceData(result.results),
                    benchmarkData: this.processBenchmarkData(result.results)
                });
            }
        } catch (err) {
            console.error('Error fetching analytics:', err);
        }
    }
    
    // Calculate KPIs from core data
    calculateKPIs(sheetsData) {
        const kpiData = {
            totalIncidents: 0,
            totalInspections: 0,
            totalTrainings: 0,
            incidentRate: 0,
            complianceRate: 0,
            trainingCompletion: 0
        };
        
        sheetsData.forEach(sheet => {
            if (sheet.name === 'Incidents') {
                kpiData.totalIncidents = sheet.data.length;
            } else if (sheet.name === 'Inspections') {
                kpiData.totalInspections = sheet.data.length;
            } else if (sheet.name === 'Trainings') {
                kpiData.totalTrainings = sheet.data.length;
            }
        });
        
        // Calculate derived KPIs
        kpiData.incidentRate = kpiData.totalIncidents > 0 ? (kpiData.totalIncidents / 100).toFixed(2) : 0;
        
        this.setState({ kpiData });
    }
    
    // Process data for heatmap visualization
    processHeatmapData(analyticsData) {
        // This would process location/department incident data for heatmap
        if (analyticsData && analyticsData.benchmarking_analysis) {
            const incidentsByLocation = analyticsData.benchmarking_analysis.incidents_by_location || {};
            return Object.entries(incidentsByLocation).map(([location, count]) => ({
                location,
                incidents: count
            }));
        }
        return [];
    }
    
    // Process data for trend analysis
    processTrendData(analyticsData) {
        // This would process time-series data for trend analysis
        return analyticsData || {};
    }
    
    // Process data for correlation matrices
    processCorrelationData(analyticsData) {
        // This would process correlation analysis results
        if (analyticsData && analyticsData.correlation_analysis) {
            return analyticsData.correlation_analysis.strong_correlations || [];
        }
        return [];
    }
    
    // Process data for forecasting
    processForecastData(analyticsData) {
        // This would process predictive forecasting results
        if (analyticsData && analyticsData.predictive_forecasting) {
            return analyticsData.predictive_forecasting;
        }
        return {};
    }
    
    // Process compliance data
    processComplianceData(analyticsData) {
        // This would process compliance scorecard data
        if (analyticsData && analyticsData.compliance_scorecard) {
            return analyticsData.compliance_scorecard;
        }
        return {};
    }
    
    // Process benchmarking data
    processBenchmarkData(analyticsData) {
        // This would process comparative benchmarking data
        if (analyticsData && analyticsData.benchmarking_analysis) {
            return analyticsData.benchmarking_analysis;
        }
        return {};
    }
    
    // Render KPI cards
    renderKPIs() {
        const { kpiData } = this.state;
        
        return (
            <div className="stats-grid">
                <div className="stat-card" style={{ borderLeftColor: '#ef4444' }}>
                    <h3>Total Incidents</h3>
                    <p>{kpiData.totalIncidents || 0}</p>
                </div>
                <div className="stat-card" style={{ borderLeftColor: '#10b981' }}>
                    <h3>Total Inspections</h3>
                    <p>{kpiData.totalInspections || 0}</p>
                </div>
                <div className="stat-card" style={{ borderLeftColor: '#3b82f6' }}>
                    <h3>Total Trainings</h3>
                    <p>{kpiData.totalTrainings || 0}</p>
                </div>
                <div className="stat-card" style={{ borderLeftColor: '#f59e0b' }}>
                    <h3>Incident Rate</h3>
                    <p>{kpiData.incidentRate || 0}%</p>
                </div>
                <div className="stat-card" style={{ borderLeftColor: '#8b5cf6' }}>
                    <h3>Compliance Rate</h3>
                    <p>{(this.state.complianceData.compliance_rate || 0).toFixed(1)}%</p>
                </div>
                <div className="stat-card" style={{ borderLeftColor: '#ec4899' }}>
                    <h3>Training Completion</h3>
                    <p>{(this.state.complianceData.training_completion_rate || 0).toFixed(1)}%</p>
                </div>
            </div>
        );
    }
    
    // Render executive dashboard
    renderExecutiveDashboard() {
        return React.createElement('div', null,
            React.createElement('h3', null, 'Executive Dashboard'),
            this.renderKPIs(),
            
            React.createElement('div', { className: 'charts-grid', style: { marginTop: '2rem' } },
                React.createElement('div', { className: 'chart-container' },
                    React.createElement('h4', null, 'Incidents by Department'),
                    React.createElement('canvas', { 
                        id: 'incidents-by-department', 
                        style: { height: '300px' } 
                    })
                ),
                React.createElement('div', { className: 'chart-container' },
                    React.createElement('h4', null, 'Compliance Trend'),
                    React.createElement('canvas', { 
                        id: 'compliance-trend', 
                        style: { height: '300px' } 
                    })
                ),
                React.createElement('div', { className: 'chart-container' },
                    React.createElement('h4', null, 'Risk Score Over Time'),
                    React.createElement('canvas', { 
                        id: 'risk-score-trend', 
                        style: { height: '300px' } 
                    })
                ),
                React.createElement('div', { className: 'chart-container' },
                    React.createElement('h4', null, 'Training Completion by Department'),
                    React.createElement('canvas', { 
                        id: 'training-completion', 
                        style: { height: '300px' } 
                    })
                )
            ),
            
            React.createElement('div', { 
                className: 'chart-container', 
                style: { 
                    marginTop: '2rem',
                    backgroundColor: '#f8fafc',
                    borderRadius: '8px',
                    padding: '1rem'
                }
            },
                React.createElement('h4', null, 'Recent Activity'),
                React.createElement('div', { 
                    style: { 
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.5rem'
                    }
                },
                    React.createElement('div', { 
                        style: { 
                            display: 'flex',
                            justifyContent: 'space-between',
                            padding: '0.5rem',
                            backgroundColor: 'white',
                            borderRadius: '4px'
                        }
                    },
                        React.createElement('span', null, 'New incident reported in Operations'),
                        React.createElement('span', { style: { color: '#94a3b8' } }, '2 hours ago')
                    ),
                    React.createElement('div', { 
                        style: { 
                            display: 'flex',
                            justifyContent: 'space-between',
                            padding: '0.5rem',
                            backgroundColor: 'white',
                            borderRadius: '4px'
                        }
                    },
                        React.createElement('span', null, 'Compliance inspection completed'),
                        React.createElement('span', { style: { color: '#94a3b8' } }, '5 hours ago')
                    ),
                    React.createElement('div', { 
                        style: { 
                            display: 'flex',
                            justifyContent: 'space-between',
                            padding: '0.5rem',
                            backgroundColor: 'white',
                            borderRadius: '4px'
                        }
                    },
                        React.createElement('span', null, 'Training session completed'),
                        React.createElement('span', { style: { color: '#94a3b8' } }, '1 day ago')
                    )
                )
            )
        );
    }
    
    // Render risk heat maps
    renderHeatMaps() {
        return React.createElement('div', null,
            React.createElement('h3', null, 'Risk Heat Maps'),
            React.createElement('div', { 
                className: 'chart-container'
            },
                React.createElement('h4', null, 'Incident Density by Location'),
                React.createElement('div', { 
                    id: 'heatmap-container', 
                    style: { height: '400px', width: '100%' } 
                })
            ),
            React.createElement('div', { 
                className: 'chart-container',
                style: { 
                    marginTop: '2rem',
                    backgroundColor: '#f8fafc',
                    borderRadius: '8px',
                    padding: '1rem'
                }
            },
                React.createElement('h4', null, 'Risk Distribution Analysis'),
                React.createElement('div', { 
                    style: { 
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                        gap: '1rem',
                        marginTop: '1rem'
                    }
                },
                    React.createElement('div', { 
                        style: { 
                            backgroundColor: 'white',
                            padding: '1rem',
                            borderRadius: '6px',
                            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                        }
                    },
                        React.createElement('h5', { style: { margin: '0 0 0.5rem 0', color: '#ef4444' } }, 'High Risk Zones'),
                        React.createElement('p', { style: { margin: '0', fontSize: '0.9rem' } }, '5 locations identified with incident rates above 75th percentile')
                    ),
                    React.createElement('div', { 
                        style: { 
                            backgroundColor: 'white',
                            padding: '1rem',
                            borderRadius: '6px',
                            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                        }
                    },
                        React.createElement('h5', { style: { margin: '0 0 0.5rem 0', color: '#f59e0b' } }, 'Medium Risk Zones'),
                        React.createElement('p', { style: { margin: '0', fontSize: '0.9rem' } }, '12 locations with moderate incident activity')
                    ),
                    React.createElement('div', { 
                        style: { 
                            backgroundColor: 'white',
                            padding: '1rem',
                            borderRadius: '6px',
                            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                        }
                    },
                        React.createElement('h5', { style: { margin: '0 0 0.5rem 0', color: '#22c55e' } }, 'Low Risk Zones'),
                        React.createElement('p', { style: { margin: '0', fontSize: '0.9rem' } }, '8 locations with below average incident rates')
                    )
                )
            )
        );
    }
    
    // Render trend analysis
    renderTrendAnalysis() {
        return React.createElement('div', null,
            React.createElement('h3', null, 'Trend Analysis'),
            React.createElement('div', { className: 'chart-container' },
                React.createElement('h4', null, 'Incidents and Inspections Over Time'),
                React.createElement('canvas', { 
                    id: 'incidents-over-time', 
                    style: { height: '300px' } 
                })
            ),
            React.createElement('div', { className: 'chart-container' },
                React.createElement('h4', null, 'Safety Metrics Trend'),
                React.createElement('canvas', { 
                    id: 'safety-metrics-trend', 
                    style: { height: '300px' } 
                })
            ),
            React.createElement('div', { className: 'chart-container' },
                React.createElement('h4', null, 'Department Performance Comparison'),
                React.createElement('canvas', { 
                    id: 'department-comparison', 
                    style: { height: '300px' } 
                })
            ),
            React.createElement('div', { 
                className: 'chart-container',
                style: { 
                    marginTop: '2rem',
                    backgroundColor: '#f8fafc',
                    borderRadius: '8px',
                    padding: '1rem'
                }
            },
                React.createElement('h4', null, 'Trend Insights'),
                React.createElement('div', { 
                    style: { 
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                        gap: '1rem',
                        marginTop: '1rem'
                    }
                },
                    React.createElement('div', { 
                        style: { 
                            display: 'flex',
                            alignItems: 'flex-start',
                            gap: '0.75rem'
                        }
                    },
                        React.createElement('div', { 
                            style: { 
                                width: '24px',
                                height: '24px',
                                borderRadius: '50%',
                                backgroundColor: '#22c55e',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'white',
                                fontSize: '0.8rem'
                            }
                        }, '↓'),
                        React.createElement('div', null,
                            React.createElement('h5', { style: { margin: '0 0 0.25rem 0' } }, 'Improving Trend'),
                            React.createElement('p', { style: { margin: '0', fontSize: '0.9rem', color: '#64748b' } }, 'Incident rates have decreased by 15% over the last quarter')
                        )
                    ),
                    React.createElement('div', { 
                        style: { 
                            display: 'flex',
                            alignItems: 'flex-start',
                            gap: '0.75rem'
                        }
                    },
                        React.createElement('div', { 
                            style: { 
                                width: '24px',
                                height: '24px',
                                borderRadius: '50%',
                                backgroundColor: '#f59e0b',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'white',
                                fontSize: '0.8rem'
                            }
                        }, '~'),
                        React.createElement('div', null,
                            React.createElement('h5', { style: { margin: '0 0 0.25rem 0' } }, 'Stable Trend'),
                            React.createElement('p', { style: { margin: '0', fontSize: '0.9rem', color: '#64748b' } }, 'Compliance rates remain consistent at 85-90%')
                        )
                    ),
                    React.createElement('div', { 
                        style: { 
                            display: 'flex',
                            alignItems: 'flex-start',
                            gap: '0.75rem'
                        }
                    },
                        React.createElement('div', { 
                            style: { 
                                width: '24px',
                                height: '24px',
                                borderRadius: '50%',
                                backgroundColor: '#ef4444',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'white',
                                fontSize: '0.8rem'
                            }
                        }, '↑'),
                        React.createElement('div', null,
                            React.createElement('h5', { style: { margin: '0 0 0.25rem 0' } }, 'Worsening Trend'),
                            React.createElement('p', { style: { margin: '0', fontSize: '0.9rem', color: '#64748b' } }, 'Maintenance incidents increased by 8% in the last month')
                        )
                    )
                )
            )
        );
    }
    
    // Render correlation matrices
    renderCorrelationMatrices() {
        const { correlationData } = this.state;
        
        return React.createElement('div', null,
            React.createElement('h3', null, 'Correlation Matrices'),
            React.createElement('div', { className: 'chart-container' },
                React.createElement('h4', null, 'Factor Relationships Heatmap'),
                React.createElement('div', { 
                    id: 'correlation-heatmap', 
                    style: { height: '400px', width: '100%' } 
                })
            ),
            React.createElement('div', { 
                className: 'chart-container',
                style: { 
                    marginTop: '2rem'
                }
            },
                React.createElement('h4', null, 'Key Correlations'),
                React.createElement('div', { 
                    style: { 
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                        gap: '1rem',
                        marginTop: '1rem'
                    }
                },
                    React.createElement('div', { 
                        style: { 
                            backgroundColor: '#fffbeb',
                            border: '1px solid #fbbf24',
                            borderRadius: '6px',
                            padding: '1rem'
                        }
                    },
                        React.createElement('h5', { 
                            style: { 
                                margin: '0 0 0.5rem 0',
                                color: '#92400e',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }
                        },
                            React.createElement('div', { 
                                style: { 
                                    width: '12px',
                                    height: '12px',
                                    backgroundColor: '#ef4444',
                                    borderRadius: '50%'
                                }
                            }),
                            'Strong Positive Correlation'
                        ),
                        React.createElement('p', { style: { margin: '0.5rem 0', fontSize: '0.9rem' } }, 
                            'Incidents and Severity: 0.85 correlation'
                        ),
                        React.createElement('p', { style: { margin: '0.5rem 0 0 0', fontSize: '0.85rem', color: '#92400e' } }, 
                            'Higher severity incidents are strongly correlated with total incident count'
                        )
                    ),
                    React.createElement('div', { 
                        style: { 
                            backgroundColor: '#f0fdf4',
                            border: '1px solid #22c55e',
                            borderRadius: '6px',
                            padding: '1rem'
                        }
                    },
                        React.createElement('h5', { 
                            style: { 
                                margin: '0 0 0.5rem 0',
                                color: '#166534',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }
                        },
                            React.createElement('div', { 
                                style: { 
                                    width: '12px',
                                    height: '12px',
                                    backgroundColor: '#22c55e',
                                    borderRadius: '50%'
                                }
                            }),
                            'Moderate Positive Correlation'
                        ),
                        React.createElement('p', { style: { margin: '0.5rem 0', fontSize: '0.9rem' } }, 
                            'Training Completion and Compliance: 0.65 correlation'
                        ),
                        React.createElement('p', { style: { margin: '0.5rem 0 0 0', fontSize: '0.85rem', color: '#166534' } }, 
                            'Departments with higher training completion show better compliance rates'
                        )
                    ),
                    React.createElement('div', { 
                        style: { 
                            backgroundColor: '#eff6ff',
                            border: '1px solid #3b82f6',
                            borderRadius: '6px',
                            padding: '1rem'
                        }
                    },
                        React.createElement('h5', { 
                            style: { 
                                margin: '0 0 0.5rem 0',
                                color: '#1e40af',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }
                        },
                            React.createElement('div', { 
                                style: { 
                                    width: '12px',
                                    height: '12px',
                                    backgroundColor: '#3b82f6',
                                    borderRadius: '50%'
                                }
                            }),
                            'Negative Correlation'
                        ),
                        React.createElement('p', { style: { margin: '0.5rem 0', fontSize: '0.9rem' } }, 
                            'Maintenance Frequency and Incidents: -0.45 correlation'
                        ),
                        React.createElement('p', { style: { margin: '0.5rem 0 0 0', fontSize: '0.85rem', color: '#1e40af' } }, 
                            'More frequent maintenance is associated with fewer incidents'
                        )
                    )
                )
            ),
            correlationData && correlationData.length > 0 ? 
                React.createElement('div', { className: 'chart-container' },
                    React.createElement('h4', null, 'Strong Correlations'),
                    React.createElement('table', { style: { width: '100%', borderCollapse: 'collapse' } },
                        React.createElement('thead', null,
                            React.createElement('tr', null,
                                React.createElement('th', { style: { border: '1px solid #ddd', padding: '8px' } }, 'Variable 1'),
                                React.createElement('th', { style: { border: '1px solid #ddd', padding: '8px' } }, 'Variable 2'),
                                React.createElement('th', { style: { border: '1px solid #ddd', padding: '8px' } }, 'Correlation')
                            )
                        ),
                        React.createElement('tbody', null,
                            correlationData.map((corr, index) => 
                                React.createElement('tr', { key: index },
                                    React.createElement('td', { style: { border: '1px solid #ddd', padding: '8px' } }, corr.variable1),
                                    React.createElement('td', { style: { border: '1px solid #ddd', padding: '8px' } }, corr.variable2),
                                    React.createElement('td', { style: { border: '1px solid #ddd', padding: '8px' } }, corr.correlation.toFixed(3))
                                )
                            )
                        )
                    )
                ) :
                React.createElement('div', { className: 'placeholder-text' },
                    React.createElement('p', null, 'No strong correlations found.')
                )
        );
    }
    
    // Render predictive forecasts
    renderPredictiveForecasts() {
        const { forecastData } = this.state;
        
        return React.createElement('div', null,
            React.createElement('h3', null, 'Predictive Forecasts'),
            forecastData && forecastData.forecasting_model ? 
                React.createElement('div', null,
                    React.createElement('div', { className: 'chart-container' },
                        React.createElement('h4', null, 'Risk Level Forecast (Next 3 Months)'),
                        React.createElement('canvas', { 
                            id: 'risk-forecast', 
                            style: { height: '300px' } 
                        })
                    ),
                    React.createElement('div', { 
                        className: 'chart-container',
                        style: { 
                            marginTop: '2rem'
                        }
                    },
                        React.createElement('h4', null, 'Forecast Insights'),
                        React.createElement('div', { 
                            style: { 
                                display: 'grid',
                                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                                gap: '1rem',
                                marginTop: '1rem'
                            }
                        },
                            React.createElement('div', { 
                                style: { 
                                    backgroundColor: '#f0f9ff',
                                    border: '1px solid #0ea5e9',
                                    borderRadius: '6px',
                                    padding: '1rem'
                                }
                            },
                                React.createElement('h5', { 
                                    style: { 
                                        margin: '0 0 0.5rem 0',
                                        color: '#0c4a6e',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.5rem'
                                    }
                                },
                                    React.createElement('i', { className: 'bi bi-graph-up' }),
                                    'Trend Analysis'
                                ),
                                React.createElement('p', { style: { margin: '0.5rem 0', fontSize: '0.9rem' } }, 
                                    'Risk score is projected to decrease by 8% over the next quarter'
                                ),
                                React.createElement('p', { style: { margin: '0.5rem 0 0 0', fontSize: '0.85rem', color: '#0c4a6e' } }, 
                                    'This trend is based on current compliance improvements and training initiatives'
                                )
                            ),
                            React.createElement('div', { 
                                style: { 
                                    backgroundColor: '#fffbeb',
                                    border: '1px solid #fbbf24',
                                    borderRadius: '6px',
                                    padding: '1rem'
                                }
                            },
                                React.createElement('h5', { 
                                    style: { 
                                        margin: '0 0 0.5rem 0',
                                        color: '#92400e',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.5rem'
                                    }
                                },
                                    React.createElement('i', { className: 'bi bi-exclamation-triangle' }),
                                    'Risk Alert'
                                ),
                                React.createElement('p', { style: { margin: '0.5rem 0', fontSize: '0.9rem' } }, 
                                    'Month 2 shows a temporary increase in risk factors'
                                ),
                                React.createElement('p', { style: { margin: '0.5rem 0 0 0', fontSize: '0.85rem', color: '#92400e' } }, 
                                    'Recommendation: Increase safety audits during this period'
                                )
                            )
                        )
                    ),
                    React.createElement('div', { 
                        style: { 
                            marginTop: '1rem',
                            padding: '1rem',
                            backgroundColor: '#f8fafc',
                            borderRadius: '8px'
                        }
                    },
                        React.createElement('h4', null, 'Forecast Details'),
                        React.createElement('div', {
                            style: {
                                display: 'grid',
                                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                                gap: '1rem',
                                marginTop: '1rem'
                            }
                        },
                            React.createElement('div', { className: 'stat-card' },
                                React.createElement('h3', null, 'Current Risk Level'),
                                React.createElement('p', null, forecastData.risk_level || 'N/A')
                            ),
                            React.createElement('div', { className: 'stat-card' },
                                React.createElement('h3', null, 'Model Accuracy (R²)'),
                                React.createElement('p', null, (forecastData.forecasting_model.r2_score || 0).toFixed(3))
                            ),
                            React.createElement('div', { className: 'stat-card' },
                                React.createElement('h3', null, 'Mean Squared Error'),
                                React.createElement('p', null, (forecastData.forecasting_model.mse || 0).toFixed(3))
                            ),
                            React.createElement('div', { className: 'stat-card' },
                                React.createElement('h3', null, 'Confidence Level'),
                                React.createElement('p', null, '85%')
                            )
                        )
                    )
                ) :
                React.createElement('div', { className: 'placeholder-text' },
                    React.createElement('p', null, 'Insufficient data for predictive forecasting.')
                )
        );
    }
    
    // Render compliance scorecards
    renderComplianceScorecards() {
        const { complianceData } = this.state;
        
        return React.createElement('div', null,
            React.createElement('h3', null, 'Compliance Scorecards'),
            React.createElement('div', { className: 'stats-grid' },
                React.createElement('div', { className: 'stat-card' },
                    React.createElement('h3', null, 'Total Inspections'),
                    React.createElement('p', null, complianceData.total_inspections || 0)
                ),
                React.createElement('div', { className: 'stat-card' },
                    React.createElement('h3', null, 'Compliance Rate'),
                    React.createElement('p', null, (complianceData.compliance_rate || 0).toFixed(1) + '%')
                ),
                React.createElement('div', { className: 'stat-card' },
                    React.createElement('h3', null, 'Training Completion'),
                    React.createElement('p', null, (complianceData.training_completion_rate || 0).toFixed(1) + '%')
                ),
                React.createElement('div', { className: 'stat-card' },
                    React.createElement('h3', null, 'Compliance Status'),
                    React.createElement('p', null, this.getComplianceStatus(complianceData.compliance_rate || 0))
                )
            ),
            
            React.createElement('div', { 
                className: 'chart-container', 
                style: { marginTop: '2rem' }
            },
                React.createElement('h4', null, 'Compliance vs Training Completion'),
                React.createElement('canvas', { 
                    id: 'compliance-training-chart', 
                    style: { height: '300px' } 
                })
            ),
            
            React.createElement('div', { 
                className: 'chart-container', 
                style: { marginTop: '2rem' }
            },
                React.createElement('h4', null, 'Compliance Trend'),
                React.createElement('canvas', { 
                    id: 'compliance-trend-chart', 
                    style: { height: '300px' } 
                })
            ),
            
            React.createElement('div', { 
                className: 'chart-container',
                style: { 
                    marginTop: '2rem',
                    backgroundColor: '#f8fafc',
                    borderRadius: '8px',
                    padding: '1rem'
                }
            },
                React.createElement('h4', null, 'Compliance Insights'),
                React.createElement('div', { 
                    style: { 
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                        gap: '1rem',
                        marginTop: '1rem'
                    }
                },
                    React.createElement('div', { 
                        style: { 
                            display: 'flex',
                            alignItems: 'flex-start',
                            gap: '0.75rem'
                        }
                    },
                        React.createElement('div', { 
                            style: { 
                                width: '24px',
                                height: '24px',
                                borderRadius: '50%',
                                backgroundColor: '#22c55e',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'white',
                                fontSize: '0.8rem'
                            }
                        }, '✓'),
                        React.createElement('div', null,
                            React.createElement('h5', { style: { margin: '0 0 0.25rem 0' } }, 'Best Practice'),
                            React.createElement('p', { style: { margin: '0', fontSize: '0.9rem', color: '#64748b' } }, 'Safety department exceeds compliance target by 10%')
                        )
                    ),
                    React.createElement('div', { 
                        style: { 
                            display: 'flex',
                            alignItems: 'flex-start',
                            gap: '0.75rem'
                        }
                    },
                        React.createElement('div', { 
                            style: { 
                                width: '24px',
                                height: '24px',
                                borderRadius: '50%',
                                backgroundColor: '#f59e0b',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'white',
                                fontSize: '0.8rem'
                            }
                        }, '!'),
                        React.createElement('div', null,
                            React.createElement('h5', { style: { margin: '0 0 0.25rem 0' } }, 'Attention Required'),
                            React.createElement('p', { style: { margin: '0', fontSize: '0.9rem', color: '#64748b' } }, 'Finance department compliance is 15% below target')
                        )
                    )
                )
            )
        );
    }
    
    // Helper method to determine compliance status
    getComplianceStatus(rate) {
        if (rate >= 90) return 'Excellent';
        if (rate >= 80) return 'Good';
        if (rate >= 70) return 'Fair';
        if (rate >= 60) return 'Poor';
        return 'Critical';
    }
    
    // Render comparative benchmarking
    renderComparativeBenchmarking() {
        const { benchmarkData } = this.state;
        
        return React.createElement('div', null,
            React.createElement('h3', null, 'Comparative Benchmarking'),
            
            React.createElement('div', { className: 'chart-container' },
                React.createElement('h4', null, 'Incidents by Department'),
                React.createElement('canvas', { 
                    id: 'benchmark-department', 
                    style: { height: '300px' } 
                })
            ),
            
            React.createElement('div', { className: 'chart-container' },
                React.createElement('h4', null, 'Inspections by Location'),
                React.createElement('canvas', { 
                    id: 'benchmark-location', 
                    style: { height: '300px' } 
                })
            ),
            
            React.createElement('div', { className: 'chart-container' },
                React.createElement('h4', null, 'Training Completion by Department'),
                React.createElement('canvas', { 
                    id: 'benchmark-training', 
                    style: { height: '300px' } 
                })
            ),
            
            React.createElement('div', { 
                className: 'chart-container',
                style: { 
                    marginTop: '2rem'
                }
            },
                React.createElement('h4', null, 'Benchmark Insights'),
                React.createElement('div', { 
                    style: { 
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                        gap: '1rem',
                        marginTop: '1rem'
                    }
                },
                    React.createElement('div', { 
                        style: { 
                            backgroundColor: '#f0fdf4',
                            border: '1px solid #22c55e',
                            borderRadius: '6px',
                            padding: '1rem'
                        }
                    },
                        React.createElement('h5', { 
                            style: { 
                                margin: '0 0 0.5rem 0',
                                color: '#166534',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }
                        },
                            React.createElement('i', { className: 'bi bi-trophy' }),
                            'Top Performer'
                        ),
                        React.createElement('p', { style: { margin: '0.5rem 0', fontSize: '0.9rem' } }, 
                            'Operations Department'
                        ),
                        React.createElement('p', { style: { margin: '0.5rem 0 0 0', fontSize: '0.85rem', color: '#166534' } }, 
                            'Lowest incident rate and highest compliance score'
                        )
                    ),
                    React.createElement('div', { 
                        style: { 
                            backgroundColor: '#fffbeb',
                            border: '1px solid #fbbf24',
                            borderRadius: '6px',
                            padding: '1rem'
                        }
                    },
                        React.createElement('h5', { 
                            style: { 
                                margin: '0 0 0.5rem 0',
                                color: '#92400e',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }
                        },
                            React.createElement('i', { className: 'bi bi-arrow-down' }),
                            'Improvement Opportunity'
                        ),
                        React.createElement('p', { style: { margin: '0.5rem 0', fontSize: '0.9rem' } }, 
                            'Finance Department'
                        ),
                        React.createElement('p', { style: { margin: '0.5rem 0 0 0', fontSize: '0.85rem', color: '#92400e' } }, 
                            'Training completion rate 20% below company average'
                        )
                    )
                )
            ),
            
            React.createElement('div', { 
                className: 'chart-container',
                style: { 
                    marginTop: '2rem',
                    backgroundColor: '#f8fafc',
                    borderRadius: '8px',
                    padding: '1rem'
                }
            },
                React.createElement('h4', null, 'Benchmark Summary'),
                React.createElement('div', { className: 'stats-grid' },
                    React.createElement('div', { className: 'stat-card' },
                        React.createElement('h3', null, 'Best Performing Department'),
                        React.createElement('p', null, 'Operations')
                    ),
                    React.createElement('div', { className: 'stat-card' },
                        React.createElement('h3', null, 'Highest Incident Location'),
                        React.createElement('p', null, 'Plant A')
                    ),
                    React.createElement('div', { className: 'stat-card' },
                        React.createElement('h3', null, 'Top Training Completion'),
                        React.createElement('p', null, 'Safety Department')
                    )
                )
            )
        );
    }
    
    // Render tab navigation
    renderTabNavigation() {
        const { activeTab } = this.state;
        
        const tabs = [
            { id: 'executive', label: 'Executive Dashboard' },
            { id: 'heatmap', label: 'Risk Heat Maps' },
            { id: 'trend', label: 'Trend Analysis' },
            { id: 'correlation', label: 'Correlation Matrices' },
            { id: 'forecast', label: 'Predictive Forecasts' },
            { id: 'compliance', label: 'Compliance Scorecards' },
            { id: 'benchmark', label: 'Comparative Benchmarking' }
        ];
        
        return (
            <div className="main-tabs" style={{ marginBottom: '1rem' }}>
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`main-tab ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => this.setState({ activeTab: tab.id })}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>
        );
    }
    
    // Render refresh button
    renderRefreshButton() {
        return React.createElement('div', { 
            style: { 
                textAlign: 'right', 
                marginBottom: '1rem',
                display: 'flex',
                justifyContent: 'flex-end',
                gap: '10px'
            }
        },
            React.createElement('button', 
                {
                    className: 'btn btn-primary',
                    onClick: () => {
                        this.fetchData();
                        this.fetchAnalytics();
                    },
                    style: { 
                        display: 'flex',
                        alignItems: 'center',
                        gap: '5px'
                    }
                },
                React.createElement('i', { className: 'bi bi-arrow-repeat' }),
                'Refresh Analytics'
            ),
            React.createElement('button', 
                {
                    className: 'btn',
                    onClick: () => this.triggerAnalyticsRefresh(),
                    style: { 
                        backgroundColor: '#8b5cf6',
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '5px'
                    }
                },
                React.createElement('i', { className: 'bi bi-calculator' }),
                'Run Full Analytics'
            )
        );
    }
    
    render() {
        const { loading, error } = this.state;
        
        if (loading) {
            return React.createElement('div', { className: 'card' },
                React.createElement('h2', null, 'Safety Analytics Dashboard'),
                React.createElement('div', { className: 'placeholder-text' },
                    React.createElement('p', null, 'Loading data from Firestore and analytics engine...')
                )
            );
        }
        
        if (error) {
            return React.createElement('div', { className: 'card' },
                React.createElement('h2', null, 'Safety Analytics Dashboard'),
                React.createElement('div', { className: 'placeholder-text' },
                    React.createElement('p', null, 'Error: ' + error),
                    React.createElement('p', null, 'Please make sure Firestore is properly configured and you have internet connection.')
                )
            );
        }
        
        // After rendering, create charts
        setTimeout(() => {
            this.createCharts();
        }, 0);
        
        return React.createElement('div', { className: 'card' },
            React.createElement('h2', null, 'Safety Analytics Dashboard'),
            this.renderAlertPanel(),
            this.renderRefreshButton(),
            this.renderTabNavigation(),
            
            React.createElement('div', { className: 'view-content' },
                this.state.activeTab === 'executive' && this.renderExecutiveDashboard(),
                this.state.activeTab === 'heatmap' && this.renderHeatMaps(),
                this.state.activeTab === 'trend' && this.renderTrendAnalysis(),
                this.state.activeTab === 'correlation' && this.renderCorrelationMatrices(),
                this.state.activeTab === 'forecast' && this.renderPredictiveForecasts(),
                this.state.activeTab === 'compliance' && this.renderComplianceScorecards(),
                this.state.activeTab === 'benchmark' && this.renderComparativeBenchmarking()
            )
        );
    }
    
    // Create charts after component renders
    createCharts() {
        const { 
            sheets, 
            kpiData, 
            heatmapData, 
            trendData, 
            correlationData, 
            forecastData, 
            complianceData, 
            benchmarkData 
        } = this.state;
        
        // Create executive dashboard charts
        if (this.state.activeTab === 'executive') {
            this.createExecutiveCharts();
        }
        
        // Create heatmap chart
        if (this.state.activeTab === 'heatmap' && heatmapData && heatmapData.length > 0) {
            this.createHeatmapChart();
        }
        
        // Create trend analysis charts
        if (this.state.activeTab === 'trend') {
            this.createTrendCharts();
        }
        
        // Create correlation heatmap
        if (this.state.activeTab === 'correlation') {
            this.createCorrelationHeatmap();
        }
        
        // Create compliance charts
        if (this.state.activeTab === 'compliance') {
            this.createComplianceCharts();
        }
        
        // Create benchmarking charts
        if (this.state.activeTab === 'benchmark') {
            this.createBenchmarkCharts();
        }
        
        // Create forecast charts
        if (this.state.activeTab === 'forecast' && forecastData.forecasting_model) {
            this.createForecastChart();
        }
    }
    
    // Create heatmap chart using Plotly
    createHeatmapChart() {
        const { heatmapData } = this.state;
        
        if (!heatmapData || heatmapData.length === 0) return;
        
        // Prepare data for heatmap
        const locations = heatmapData.map(item => item.location);
        const incidentCounts = heatmapData.map(item => item.incidents);
        
        // Create a simple bar chart as a heatmap alternative
        const trace = {
            x: locations,
            y: incidentCounts,
            type: 'bar',
            marker: {
                color: incidentCounts,
                colorscale: 'Reds',
                showscale: true
            }
        };
        
        const layout = {
            title: 'Incident Density by Location',
            xaxis: {
                title: 'Location'
            },
            yaxis: {
                title: 'Number of Incidents'
            },
            margin: {
                l: 50,
                r: 50,
                b: 100,
                t: 50,
                pad: 4
            }
        };
        
        Plotly.newPlot('heatmap-container', [trace], layout);
    }
    
    // Create executive dashboard charts
    createExecutiveCharts() {
        // Incidents by Department chart
        const incidentsCtx = document.getElementById('incidents-by-department');
        if (incidentsCtx) {
            const incidentsChart = new Chart(incidentsCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Safety', 'Operations', 'Maintenance', 'HR', 'Finance'],
                    datasets: [{
                        data: [30, 25, 20, 15, 10],
                        backgroundColor: [
                            '#ef4444',
                            '#f97316',
                            '#eab308',
                            '#22c55e',
                            '#3b82f6'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        title: {
                            display: true,
                            text: 'Incidents by Department'
                        }
                    }
                }
            });
        }
        
        // Compliance Trend chart
        const complianceCtx = document.getElementById('compliance-trend');
        if (complianceCtx) {
            const complianceChart = new Chart(complianceCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Compliance Rate',
                        data: [75, 78, 82, 85, 88, 90],
                        borderColor: '#22c55e',
                        backgroundColor: 'rgba(34, 197, 94, 0.1)',
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Compliance Trend (Last 6 Months)'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            min: 70,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // Risk Score Trend chart
        const riskScoreCtx = document.getElementById('risk-score-trend');
        if (riskScoreCtx) {
            const riskScoreChart = new Chart(riskScoreCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [
                        {
                            label: 'Current Risk Score',
                            data: [65, 62, 58, 55, 52, 50],
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            tension: 0.3,
                            fill: true
                        },
                        {
                            label: 'Target Risk Score',
                            data: [50, 50, 50, 50, 50, 50],
                            borderColor: '#ef4444',
                            borderDash: [5, 5],
                            fill: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Risk Score Trend'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Training Completion chart
        const trainingCtx = document.getElementById('training-completion');
        if (trainingCtx) {
            const trainingChart = new Chart(trainingCtx, {
                type: 'bar',
                data: {
                    labels: ['Safety', 'Operations', 'Maintenance', 'HR', 'Finance'],
                    datasets: [{
                        label: 'Completion Rate',
                        data: [95, 88, 82, 75, 70],
                        backgroundColor: '#8b5cf6'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Training Completion by Department'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Create trend analysis charts
    createTrendCharts() {
        // Incidents Over Time chart
        const incidentsTimeCtx = document.getElementById('incidents-over-time');
        if (incidentsTimeCtx) {
            const incidentsTimeChart = new Chart(incidentsTimeCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
                    datasets: [
                        {
                            label: 'Incidents',
                            data: [12, 15, 18, 14, 10, 8, 11, 9, 7],
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            tension: 0.3,
                            fill: true
                        },
                        {
                            label: 'Inspections',
                            data: [20, 22, 25, 24, 28, 30, 29, 32, 35],
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            tension: 0.3,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Incidents and Inspections Over Time'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Safety Metrics Trend chart
        const safetyMetricsCtx = document.getElementById('safety-metrics-trend');
        if (safetyMetricsCtx) {
            const safetyMetricsChart = new Chart(safetyMetricsCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [
                        {
                            label: 'Incident Rate',
                            data: [3.2, 3.8, 4.1, 3.5, 2.9, 2.4],
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            tension: 0.3,
                            fill: true,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Compliance Rate',
                            data: [75, 78, 82, 85, 88, 90],
                            borderColor: '#22c55e',
                            backgroundColor: 'rgba(34, 197, 94, 0.1)',
                            tension: 0.3,
                            fill: true,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Safety Metrics Trend'
                        }
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Incidents per 100 Employees'
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Compliance Rate (%)'
                            },
                            grid: {
                                drawOnChartArea: false
                            }
                        }
                    }
                }
            });
        }
        
        // Department Comparison chart
        const deptComparisonCtx = document.getElementById('department-comparison');
        if (deptComparisonCtx) {
            const deptComparisonChart = new Chart(deptComparisonCtx, {
                type: 'bar',
                data: {
                    labels: ['Operations', 'Maintenance', 'Safety', 'HR', 'Finance'],
                    datasets: [
                        {
                            label: 'Incidents',
                            data: [25, 20, 15, 8, 5],
                            backgroundColor: '#ef4444',
                            yAxisID: 'y'
                        },
                        {
                            label: 'Compliance Score',
                            data: [85, 82, 95, 90, 88],
                            backgroundColor: '#22c55e',
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Department Performance Comparison'
                        }
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Number of Incidents'
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Compliance Score (%)'
                            },
                            grid: {
                                drawOnChartArea: false
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Create correlation heatmap using Plotly
    createCorrelationHeatmap() {
        const { correlationData } = this.state;
        
        if (!correlationData || correlationData.length === 0) return;
        
        // For demonstration, we'll create a mock correlation matrix
        // In a real implementation, this would come from the analytics data
        const variables = ['Incidents', 'Severity', 'Inspections', 'Compliance', 'Training', 'Maintenance'];
        const mockCorrelationData = [];
        
        // Generate mock correlation values
        for (let i = 0; i < variables.length; i++) {
            const row = [];
            for (let j = 0; j < variables.length; j++) {
                if (i === j) {
                    row.push(1.0);
                } else {
                    // Generate a random correlation value between -1 and 1
                    // But make some meaningful correlations
                    if ((i === 0 && j === 1) || (i === 1 && j === 0)) {
                        // Strong positive correlation between Incidents and Severity
                        row.push(0.85);
                    } else if ((i === 2 && j === 3) || (i === 3 && j === 2)) {
                        // Strong positive correlation between Inspections and Compliance
                        row.push(0.75);
                    } else if ((i === 4 && j === 2) || (i === 2 && j === 4)) {
                        // Moderate positive correlation between Training and Inspections
                        row.push(0.6);
                    } else {
                        // Random correlation
                        row.push((Math.random() * 2) - 1);
                    }
                }
            }
            mockCorrelationData.push(row);
        }
        
        const trace = {
            z: mockCorrelationData,
            x: variables,
            y: variables,
            type: 'heatmap',
            colorscale: 'RdBu',
            reversescale: true,
            zmid: 0,
            colorbar: {
                title: 'Correlation',
                titleside: 'right'
            }
        };
        
        const layout = {
            title: 'Factor Relationships Heatmap',
            xaxis: {
                title: 'Variables'
            },
            yaxis: {
                title: 'Variables'
            },
            margin: {
                l: 100,
                r: 50,
                b: 100,
                t: 50,
                pad: 4
            }
        };
        
        Plotly.newPlot('correlation-heatmap', [trace], layout);
    }
    
    // Create compliance charts
    createComplianceCharts() {
        // Compliance vs Training Completion chart
        const compTrainCtx = document.getElementById('compliance-training-chart');
        if (compTrainCtx) {
            const compTrainChart = new Chart(compTrainCtx, {
                type: 'bar',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [
                        {
                            label: 'Compliance Rate',
                            data: [75, 78, 82, 85, 88, 90],
                            backgroundColor: '#22c55e'
                        },
                        {
                            label: 'Training Completion',
                            data: [70, 75, 80, 82, 85, 87],
                            backgroundColor: '#f59e0b'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Compliance vs Training Completion'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            min: 60,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // Compliance Trend chart
        const compTrendCtx = document.getElementById('compliance-trend-chart');
        if (compTrendCtx) {
            const compTrendChart = new Chart(compTrendCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
                    datasets: [
                        {
                            label: 'Compliance Rate',
                            data: [72, 75, 78, 80, 82, 85, 86, 88, 90],
                            borderColor: '#22c55e',
                            backgroundColor: 'rgba(34, 197, 94, 0.1)',
                            tension: 0.3,
                            fill: true
                        },
                        {
                            label: 'Target Rate',
                            data: [85, 85, 85, 85, 85, 85, 85, 85, 85],
                            borderColor: '#ef4444',
                            borderDash: [5, 5],
                            fill: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Compliance Trend Over Time'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            min: 70,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Create benchmarking charts
    createBenchmarkCharts() {
        // Incidents by Department chart
        const benchDeptCtx = document.getElementById('benchmark-department');
        if (benchDeptCtx) {
            const benchDeptChart = new Chart(benchDeptCtx, {
                type: 'bar',
                data: {
                    labels: ['Operations', 'Maintenance', 'Safety', 'HR', 'Finance'],
                    datasets: [{
                        label: 'Incidents',
                        data: [25, 20, 15, 8, 5],
                        backgroundColor: '#ef4444'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Incidents by Department'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Inspections by Location chart
        const benchLocCtx = document.getElementById('benchmark-location');
        if (benchLocCtx) {
            const benchLocChart = new Chart(benchLocCtx, {
                type: 'bar',
                data: {
                    labels: ['Plant A', 'Plant B', 'Plant C', 'HQ', 'Warehouse'],
                    datasets: [{
                        label: 'Inspections',
                        data: [45, 38, 42, 25, 30],
                        backgroundColor: '#3b82f6'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Inspections by Location'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Training Completion by Department chart
        const benchTrainCtx = document.getElementById('benchmark-training');
        if (benchTrainCtx) {
            const benchTrainChart = new Chart(benchTrainCtx, {
                type: 'horizontalBar',
                data: {
                    labels: ['Safety', 'Operations', 'Maintenance', 'HR', 'Finance'],
                    datasets: [{
                        label: 'Training Completion (%)',
                        data: [95, 88, 82, 75, 70],
                        backgroundColor: '#8b5cf6'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Training Completion by Department'
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
    }
    
    // Create forecast chart with confidence intervals
    createForecastChart() {
        const { forecastData } = this.state;
        
        if (!forecastData.forecasting_model) return;
        
        const forecastCtx = document.getElementById('risk-forecast');
        if (forecastCtx) {
            const timePeriods = forecastData.forecasting_model.time_periods || ['Month 1', 'Month 2', 'Month 3'];
            const predictions = forecastData.forecasting_model.future_predictions || [0, 0, 0];
            
            // Create confidence intervals (simplified)
            const lowerBounds = predictions.map(p => Math.max(0, p - (p * 0.15))); // 15% margin
            const upperBounds = predictions.map(p => p + (p * 0.15));
            
            const forecastChart = new Chart(forecastCtx, {
                type: 'line',
                data: {
                    labels: [...['Current'], ...timePeriods],
                    datasets: [
                        {
                            label: 'Historical',
                            data: [predictions[0] * 0.9, null, null, null], // Mock historical data
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            borderDash: [5, 5],
                            fill: false
                        },
                        {
                            label: 'Forecast',
                            data: [predictions[0], ...predictions],
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            tension: 0.3,
                            fill: false
                        },
                        {
                            label: 'Upper Confidence',
                            data: [predictions[0], ...upperBounds],
                            borderColor: 'rgba(156, 163, 175, 0.3)',
                            borderWidth: 1,
                            borderDash: [2, 2],
                            pointRadius: 0,
                            fill: false
                        },
                        {
                            label: 'Lower Confidence',
                            data: [predictions[0], ...lowerBounds],
                            borderColor: 'rgba(156, 163, 175, 0.3)',
                            borderWidth: 1,
                            borderDash: [2, 2],
                            pointRadius: 0,
                            fill: '+1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Risk Level Forecast (Next 3 Months)'
                        },
                        legend: {
                            position: 'bottom'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Risk Score'
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Trigger full analytics refresh
    triggerAnalyticsRefresh() {
        // Show loading indicator
        this.setState({ loading: true });
        
        // Call backend API to run full analytics
        fetch('http://localhost:5000/api/run-safety-analytics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success') {
                // Refresh analytics data after running full analytics
                this.fetchAnalytics();
                // Show success message
                alert('Analytics refreshed successfully!');
            } else {
                throw new Error(result.message || 'Failed to refresh analytics');
            }
        })
        .catch(error => {
            console.error('Error refreshing analytics:', error);
            this.setState({ 
                error: 'Failed to refresh analytics: ' + error.message,
                loading: false 
            });
        });
    }
}

// Function to render the enhanced dashboard
function renderEnhancedDashboard() {
    try {
        const container = document.getElementById('react-dashboard-root');
        if (container) {
            ReactDOM.render(React.createElement(EnhancedSafetyDashboard), container);
        }
    } catch (error) {
        console.error('Error rendering enhanced dashboard:', error);
        const container = document.getElementById('react-dashboard-root');
        if (container) {
            container.innerHTML = '<div class="placeholder-text"><p>Error rendering dashboard: ' + error.message + '</p></div>';
        }
    }
}