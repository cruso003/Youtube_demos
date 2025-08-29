import React, { JSX } from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';


export default function Home(): JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title="NexusAI Documentation"
      description="Official documentation for NexusAI - The Universal AI Agent Platform for Africa">
      <main>
        <div className="hero hero--primary">
          <div className="container">
            <h1 className="hero__title">NexusAI Documentation</h1>
            <p className="hero__subtitle">
              Official API documentation and developer guides for NexusAI - The Universal AI Agent Platform built for Africa
            </p>
            <div className="buttons">
              <Link
                className="button button--secondary button--lg"
                to="/docs/getting-started">
                Get Started
              </Link>
              <Link
                className="button button--primary button--lg"
                href="https://nexus.bits-innovate.com">
                Main Website
              </Link>
            </div>
          </div>
        </div>
        <section className="margin-top--lg margin-bottom--lg">
          <div className="container">
            <div className="row">
              <div className="col col--4">
                <div className="text--center">
                  <h3>📚 API Reference</h3>
                  <p>Complete REST API documentation with examples and response formats.</p>
                  <Link className="button button--outline button--primary" to="/docs/api">
                    View API Docs
                  </Link>
                </div>
              </div>
              <div className="col col--4">
                <div className="text--center">
                  <h3>🛠️ SDK Guides</h3>
                  <p>JavaScript and Python SDKs with installation guides and examples.</p>
                  <Link className="button button--outline button--primary" to="/docs/sdks">
                    Browse SDKs
                  </Link>
                </div>
              </div>
              <div className="col col--4">
                <div className="text--center">
                  <h3> Getting Started</h3>
                  <p>Quick setup guide and best practices for African developers.</p>
                  <Link className="button button--outline button--primary" to="/docs/getting-started">
                    Get Started
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}