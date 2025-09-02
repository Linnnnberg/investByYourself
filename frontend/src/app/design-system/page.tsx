/**
 * Design System Demo Page for investByYourself Platform
 * Showcases all design system components and tokens
 */

'use client';

import React from 'react';
import { Button, Card, CardHeader, CardContent, CardFooter } from '../../design-system/components';
import { colors, typography, spacing, designSystem } from '../../design-system';

export default function DesignSystemPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            investByYourself Design System
          </h1>
          <p className="text-xl text-gray-600">
            Professional financial platform design system with consistent components and tokens
          </p>
        </div>

        {/* Colors Section */}
        <section className="mb-16">
          <h2 className="text-3xl font-semibold text-gray-900 mb-8">Color Palette</h2>

          {/* Primary Colors */}
          <div className="mb-8">
            <h3 className="text-xl font-medium text-gray-800 mb-4">Primary Colors</h3>
            <div className="grid grid-cols-10 gap-2">
              {Object.entries(colors.primary).map(([shade, color]) => (
                <div key={shade} className="text-center">
                  <div
                    className="w-16 h-16 rounded-lg border border-gray-200 mb-2"
                    style={{ backgroundColor: color }}
                  />
                  <p className="text-xs font-mono text-gray-600">{shade}</p>
                  <p className="text-xs font-mono text-gray-500">{color}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Semantic Colors */}
          <div className="mb-8">
            <h3 className="text-xl font-medium text-gray-800 mb-4">Semantic Colors</h3>
            <div className="grid grid-cols-5 gap-4">
              <div className="text-center">
                <div
                  className="w-20 h-20 rounded-lg border border-gray-200 mb-2"
                  style={{ backgroundColor: colors.financial.profit }}
                />
                <p className="font-medium text-gray-800">Profit</p>
                <p className="text-sm font-mono text-gray-600">{colors.financial.profit}</p>
              </div>
              <div className="text-center">
                <div
                  className="w-20 h-20 rounded-lg border border-gray-200 mb-2"
                  style={{ backgroundColor: colors.financial.loss }}
                />
                <p className="font-medium text-gray-800">Loss</p>
                <p className="text-sm font-mono text-gray-600">{colors.financial.loss}</p>
              </div>
              <div className="text-center">
                <div
                  className="w-20 h-20 rounded-lg border border-gray-200 mb-2"
                  style={{ backgroundColor: colors.financial.alert }}
                />
                <p className="font-medium text-gray-800">Alert</p>
                <p className="text-sm font-mono text-gray-600">{colors.financial.alert}</p>
              </div>
              <div className="text-center">
                <div
                  className="w-20 h-20 rounded-lg border border-gray-200 mb-2"
                  style={{ backgroundColor: colors.financial.info }}
                />
                <p className="font-medium text-gray-800">Info</p>
                <p className="text-sm font-mono text-gray-600">{colors.financial.info}</p>
              </div>
              <div className="text-center">
                <div
                  className="w-20 h-20 rounded-lg border border-gray-200 mb-2"
                  style={{ backgroundColor: colors.financial.neutral }}
                />
                <p className="font-medium text-gray-800">Neutral</p>
                <p className="text-sm font-mono text-gray-600">{colors.financial.neutral}</p>
              </div>
            </div>
          </div>
        </section>

        {/* Typography Section */}
        <section className="mb-16">
          <h2 className="text-3xl font-semibold text-gray-900 mb-8">Typography</h2>

          {/* Display Styles */}
          <div className="mb-8">
            <h3 className="text-xl font-medium text-gray-800 mb-4">Display Styles</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">Display Large</p>
                <h1 style={{
                  fontSize: typography.textStyles.display.large.fontSize,
                  fontWeight: typography.textStyles.display.large.fontWeight,
                  lineHeight: typography.textStyles.display.large.lineHeight,
                  letterSpacing: typography.textStyles.display.large.letterSpacing,
                }}>
                  Display Large Heading
                </h1>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Display Medium</p>
                <h2 style={{
                  fontSize: typography.textStyles.display.medium.fontSize,
                  fontWeight: typography.textStyles.display.medium.fontWeight,
                  lineHeight: typography.textStyles.display.medium.lineHeight,
                  letterSpacing: typography.textStyles.display.medium.letterSpacing,
                }}>
                  Display Medium Heading
                </h2>
              </div>
            </div>
          </div>

          {/* Heading Styles */}
          <div className="mb-8">
            <h3 className="text-xl font-medium text-gray-800 mb-4">Heading Styles</h3>
            <div className="space-y-4">
              {Object.entries(typography.textStyles.heading).map(([level, style]) => (
                <div key={level}>
                  <p className="text-sm text-gray-600 mb-1">{level.toUpperCase()}</p>
                  <div style={{
                    fontSize: style.fontSize,
                    fontWeight: style.fontWeight,
                    lineHeight: style.lineHeight,
                    letterSpacing: style.letterSpacing,
                  }}>
                    {level.charAt(0).toUpperCase() + level.slice(1)} Heading
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Body Styles */}
          <div className="mb-8">
            <h3 className="text-xl font-medium text-gray-800 mb-4">Body Styles</h3>
            <div className="space-y-4">
              {Object.entries(typography.textStyles.body).map(([size, style]) => (
                <div key={size}>
                  <p className="text-sm text-gray-600 mb-1">Body {size.charAt(0).toUpperCase() + size.slice(1)}</p>
                  <p style={{
                    fontSize: style.fontSize,
                    fontWeight: style.fontWeight,
                    lineHeight: style.lineHeight,
                    letterSpacing: style.letterSpacing,
                  }}>
                    This is body {size} text with proper line height and spacing for optimal readability.
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Spacing Section */}
        <section className="mb-16">
          <h2 className="text-3xl font-semibold text-gray-900 mb-8">Spacing Scale</h2>

          <div className="grid grid-cols-2 gap-8">
            {/* Base Spacing */}
            <div>
              <h3 className="text-xl font-medium text-gray-800 mb-4">Base Spacing</h3>
              <div className="space-y-2">
                {Object.entries(spacing).filter(([key]) => !['component', 'layout', 'responsive', 'utility'].includes(key)).map(([size, value]) => (
                  <div key={size} className="flex items-center">
                    <div
                      className="bg-blue-500 rounded"
                      style={{ width: value, height: '1rem' }}
                    />
                    <span className="ml-3 font-mono text-sm text-gray-600">
                      {size}: {value}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Component Spacing */}
            <div>
              <h3 className="text-xl font-medium text-gray-800 mb-4">Component Spacing</h3>
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  Button Gap: {spacing.component.button.gap}
                </p>
                <p className="text-sm text-gray-600">
                  Card Padding: {spacing.component.card.padding}
                </p>
                <p className="text-sm text-gray-600">
                  Form Gap: {spacing.component.form.gap}
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Components Section */}
        <section className="mb-16">
          <h2 className="text-3xl font-semibold text-gray-900 mb-8">Components</h2>

          {/* Buttons */}
          <div className="mb-12">
            <h3 className="text-xl font-medium text-gray-800 mb-6">Buttons</h3>

            {/* Button Variants */}
            <div className="mb-6">
              <h4 className="text-lg font-medium text-gray-700 mb-4">Variants</h4>
              <div className="flex flex-wrap gap-4">
                <Button variant="primary">Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="outline">Outline</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="danger">Danger</Button>
                <Button variant="success">Success</Button>
              </div>
            </div>

            {/* Button Sizes */}
            <div className="mb-6">
              <h4 className="text-lg font-medium text-gray-700 mb-4">Sizes</h4>
              <div className="flex flex-wrap items-center gap-4">
                <Button size="small">Small</Button>
                <Button size="medium">Medium</Button>
                <Button size="large">Large</Button>
              </div>
            </div>

            {/* Button States */}
            <div className="mb-6">
              <h4 className="text-lg font-medium text-gray-700 mb-4">States</h4>
              <div className="flex flex-wrap gap-4">
                <Button loading>Loading</Button>
                <Button disabled>Disabled</Button>
                <Button variant="outline" fullWidth>Full Width</Button>
              </div>
            </div>
          </div>

          {/* Cards */}
          <div className="mb-12">
            <h3 className="text-xl font-medium text-gray-800 mb-6">Cards</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Default Card */}
              <Card>
                <CardHeader>
                  <h4 className="text-lg font-semibold">Default Card</h4>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">
                    This is a default card with header, content, and footer sections.
                  </p>
                </CardContent>
                <CardFooter>
                  <Button size="small">Action</Button>
                </CardFooter>
              </Card>

              {/* Elevated Card */}
              <Card variant="elevated">
                <CardContent>
                  <h4 className="text-lg font-semibold mb-2">Elevated Card</h4>
                  <p className="text-gray-600">
                    This card has a more prominent shadow for emphasis.
                  </p>
                </CardContent>
              </Card>

              {/* Interactive Card */}
              <Card variant="interactive" hoverable>
                <CardContent>
                  <h4 className="text-lg font-semibold mb-2">Interactive Card</h4>
                  <p className="text-gray-600">
                    Hover over this card to see the interactive effects.
                  </p>
                </CardContent>
              </Card>

              {/* Financial Card */}
              <Card variant="financial">
                <CardContent>
                  <h4 className="text-lg font-semibold mb-2">Financial Card</h4>
                  <p className="text-gray-600">
                    This card has a financial theme with gradient background.
                  </p>
                </CardContent>
              </Card>

              {/* Outlined Card */}
              <Card variant="outlined">
                <CardContent>
                  <h4 className="text-lg font-semibold mb-2">Outlined Card</h4>
                  <p className="text-gray-600">
                    This card has a prominent border without shadow.
                  </p>
                </CardContent>
              </Card>

              {/* Custom Padding Card */}
              <Card padding="large">
                <CardContent>
                  <h4 className="text-lg font-semibold mb-2">Large Padding</h4>
                  <p className="text-gray-600">
                    This card has larger padding for more spacious content.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Design System Info */}
        <section className="mb-16">
          <h2 className="text-3xl font-semibold text-gray-900 mb-8">Design System Information</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <Card>
              <CardHeader>
                <h3 className="text-xl font-semibold">System Details</h3>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p><strong>Name:</strong> {designSystem.name}</p>
                  <p><strong>Version:</strong> {designSystem.version}</p>
                  <p><strong>Description:</strong> {designSystem.description}</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <h3 className="text-xl font-semibold">Design Principles</h3>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(designSystem.principles).map(([key, principle]) => (
                    <p key={key}><strong>{key.charAt(0).toUpperCase() + key.slice(1)}:</strong> {principle}</p>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </section>
      </div>
    </div>
  );
}
