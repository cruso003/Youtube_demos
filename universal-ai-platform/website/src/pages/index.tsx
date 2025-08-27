import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HeroSection() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero', styles.heroBanner)}>
      <div className="container">
        <div className={styles.heroContent}>
          <div className={styles.heroText}>
            <Heading as="h1" className={styles.heroTitle}>
              Universal AI Agent Platform for Any Industry
            </Heading>
            <p className={styles.heroSubtitle}>
              Integrate multimodal AI agents (voice, vision, text) into your applications 
              without building AI infrastructure. Enterprise-ready SaaS platform with 
              flexible business logic adapters.
            </p>
            <div className={styles.heroButtons}>
              <Link
                className="button button--primary button--lg"
                to="/docs/getting-started">
                Start Building with Our API
              </Link>
              <Link
                className="button button--secondary button--lg"
                to="/docs/examples/language-learning">
                View Examples
              </Link>
            </div>
          </div>
          <div className={styles.heroDemo}>
            <div className={styles.codeExample}>
              <div className={styles.codeHeader}>
                <span>Quick Start</span>
              </div>
              <pre><code>{`from universal_ai_sdk import create_simple_agent

# Create multimodal agent
session = create_simple_agent(
    instructions="You are a helpful assistant",
    capabilities=["text", "voice", "vision"]
)

# Send message and get response
session.send_message("Hello!")
response = session.wait_for_response()
print(response.content)`}</code></pre>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

function FeaturesSection() {
  const features = [
    {
      title: 'Multimodal Capabilities',
      icon: '🎯',
      description: 'Voice, vision, and text processing in one unified platform. Speech-to-text, text-to-speech, image analysis, and natural language conversation.',
    },
    {
      title: 'Business Logic Adapters',
      icon: '🔧',
      description: 'Pluggable framework for customizing agent behavior. Pre-built adapters for language learning, emergency services, and custom domain logic.',
    },
    {
      title: 'Usage Tracking & Billing',
      icon: '📊',
      description: 'Real-time tracking of sessions, messages, images, and duration. Automated billing with flexible pricing plans for every business size.',
    },
    {
      title: 'Enterprise SDKs',
      icon: '⚡',
      description: 'Full-featured Python and JavaScript SDKs with async support, error handling, and high-level abstractions for rapid development.',
    },
  ];

  return (
    <section className={styles.features}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2">Why Choose Universal AI Platform?</Heading>
          <p>Everything you need to integrate AI agents into your applications</p>
        </div>
        <div className={styles.featuresGrid}>
          {features.map((feature, idx) => (
            <div key={idx} className={styles.featureCard}>
              <div className={styles.featureIcon}>{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function UseCasesSection() {
  const useCases = [
    {
      title: 'Language Learning',
      description: 'Interactive conversation practice with voice feedback, pronunciation correction, and adaptive difficulty levels.',
      technologies: ['Speech Recognition', 'Natural Language', 'Adaptive Learning'],
      demoLink: '/docs/examples/language-learning',
    },
    {
      title: 'Emergency Services',
      description: 'Real-time emergency dispatch with location extraction, priority escalation, and automated call logging.',
      technologies: ['Voice Processing', 'Location Services', 'Priority Routing'],
      demoLink: '/docs/examples/language-learning',
    },
    {
      title: 'Healthcare',
      description: 'Patient intake, symptom assessment, and medical record integration with HIPAA compliance.',
      technologies: ['Medical NLP', 'Secure Processing', 'Integration APIs'],
      demoLink: '/docs/examples/language-learning',
    },
    {
      title: 'Customer Support',
      description: 'Intelligent support agents with multi-channel communication, ticket routing, and knowledge base integration.',
      technologies: ['Multi-Channel', 'Knowledge Base', 'Sentiment Analysis'],
      demoLink: '/docs/examples/language-learning',
    },
  ];

  return (
    <section className={styles.useCases}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2">Proven Use Cases Across Industries</Heading>
          <p>Real-world applications powered by our platform</p>
        </div>
        <div className={styles.useCasesGrid}>
          {useCases.map((useCase, idx) => (
            <div key={idx} className={styles.useCaseCard}>
              <h3>{useCase.title}</h3>
              <p>{useCase.description}</p>
              <div className={styles.technologies}>
                {useCase.technologies.map((tech, techIdx) => (
                  <span key={techIdx} className={styles.techTag}>{tech}</span>
                ))}
              </div>
              <Link to={useCase.demoLink} className={styles.useCaseLink}>
                View Demo →
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function PricingSection() {
  const plans = [
    {
      name: 'Starter',
      price: '$49',
      period: '/month',
      description: 'Perfect for small projects and prototypes',
      features: [
        '1,000 API calls/month',
        'Text & Voice capabilities',
        'Basic adapters',
        'Email support',
        'SDK access',
      ],
      popular: false,
    },
    {
      name: 'Professional',
      price: '$199',
      period: '/month',
      description: 'Ideal for growing businesses and applications',
      features: [
        '25,000 API calls/month',
        'All multimodal capabilities',
        'Custom adapters',
        'Priority support',
        'Advanced analytics',
        'Deployment guides',
      ],
      popular: true,
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      description: 'For large-scale applications with custom needs',
      features: [
        'Unlimited API calls',
        'White-label solutions',
        'Custom integrations',
        'Dedicated support team',
        'SLA guarantees',
        'On-premise deployment',
      ],
      popular: false,
    },
  ];

  return (
    <section className={styles.pricing}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2">Simple, Transparent Pricing</Heading>
          <p>Choose the plan that fits your needs</p>
        </div>
        <div className={styles.pricingGrid}>
          {plans.map((plan, idx) => (
            <div key={idx} className={clsx(styles.pricingCard, plan.popular && styles.popularCard)}>
              {plan.popular && <div className={styles.popularBadge}>Most Popular</div>}
              <h3>{plan.name}</h3>
              <div className={styles.priceSection}>
                <span className={styles.price}>{plan.price}</span>
                <span className={styles.period}>{plan.period}</span>
              </div>
              <p className={styles.planDescription}>{plan.description}</p>
              <ul className={styles.featuresList}>
                {plan.features.map((feature, featureIdx) => (
                  <li key={featureIdx}>{feature}</li>
                ))}
              </ul>
              <Link
                to="/docs/getting-started"
                className={clsx(
                  'button button--lg',
                  plan.popular ? 'button--primary' : 'button--secondary'
                )}
              >
                Get Started
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function LiveDemoSection() {
  return (
    <section className={styles.liveDemo}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2">See It In Action</Heading>
          <p>Try our live demos to experience the platform capabilities</p>
        </div>
        <div className={styles.demoGrid}>
          <div className={styles.demoCard}>
            <h3>🎓 Language Learning Assistant</h3>
            <p>Interactive conversation practice with a Spanish tutor. Features voice recognition, pronunciation feedback, and adaptive learning.</p>
            <div className={styles.demoActions}>
              <Link to="/docs/examples/language-learning" className="button button--primary">
                Try Demo
              </Link>
              <Link to="https://github.com/cruso003/Youtube_demos/tree/main/universal-ai-platform/demos/language_learning" className="button button--secondary">
                View Code
              </Link>
            </div>
          </div>
          <div className={styles.demoCard}>
            <h3>🚨 Emergency Services Dispatcher</h3>
            <p>Real-time emergency response system with location extraction, priority routing, and automated call logging.</p>
            <div className={styles.demoActions}>
              <Link to="/docs/examples/language-learning" className="button button--primary">
                Try Demo
              </Link>
              <Link to="https://github.com/cruso003/Youtube_demos/tree/main/universal-ai-platform/demos/emergency_services" className="button button--secondary">
                View Code
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function CTASection() {
  return (
    <section className={styles.cta}>
      <div className="container">
        <div className={styles.ctaContent}>
          <Heading as="h2">Ready to Build the Future?</Heading>
          <p>Join thousands of developers building with our Universal AI Platform</p>
          <div className={styles.ctaButtons}>
            <Link
              className="button button--primary button--lg"
              to="/docs/getting-started">
              Start Building with Our API
            </Link>
            <Link
              className="button button--secondary button--lg"
              to="/docs/examples/language-learning">
              Explore Examples
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title="Universal AI Agent Platform"
      description="Integrate multimodal AI agents into any application without building infrastructure. Enterprise-ready SaaS platform with voice, vision, and text capabilities.">
      <HeroSection />
      <main>
        <FeaturesSection />
        <UseCasesSection />
        <LiveDemoSection />
        <PricingSection />
        <CTASection />
      </main>
    </Layout>
  );
}
