export function finiteValues(
  values: Array<number | null | undefined>,
): number[] {
  return values.filter(
    (
      value
    ): value is number => (
      typeof value === "number"
      && Number.isFinite(
        value
      )
    )
  );
}


export function mean(
  values: number[],
): number | null {
  if (
    values.length === 0
  ) {
    return null;
  }

  return (
    values.reduce(
      (
        total,
        value,
      ) => total + value,
      0,
    )
    / values.length
  );
}


export function sampleStandardDeviation(
  values: number[],
): number | null {
  if (
    values.length < 2
  ) {
    return null;
  }

  const average = mean(
    values
  );

  if (
    average === null
  ) {
    return null;
  }

  const squared = values.reduce(
    (
      total,
      value,
    ) => (
      total
      + (
        value - average
      ) ** 2
    ),
    0,
  );

  return Math.sqrt(
    squared
    / (
      values.length - 1
    )
  );
}


export function pearsonCorrelation(
  x: number[],
  y: number[],
): number | null {
  if (
    x.length !== y.length
    || x.length < 2
  ) {
    return null;
  }

  const meanX = mean(
    x
  );

  const meanY = mean(
    y
  );

  if (
    meanX === null
    || meanY === null
  ) {
    return null;
  }

  let numerator = 0;
  let sumSquareX = 0;
  let sumSquareY = 0;

  for (
    let index = 0;
    index < x.length;
    index += 1
  ) {
    const dx = (
      x[index] - meanX
    );

    const dy = (
      y[index] - meanY
    );

    numerator += (
      dx * dy
    );

    sumSquareX += (
      dx ** 2
    );

    sumSquareY += (
      dy ** 2
    );
  }

  const denominator = Math.sqrt(
    sumSquareX
    * sumSquareY
  );

  if (
    denominator < 1e-12
  ) {
    return null;
  }

  const result = (
    numerator
    / denominator
  );

  return (
    Number.isFinite(
      result
    )
      ? result
      : null
  );
}


export type LinearRegressionResult = {
  slope: number;
  intercept: number;
  change: number;
  rSquared: number;
};


export function linearRegression(
  values: number[],
): LinearRegressionResult | null {
  if (
    values.length < 2
  ) {
    return null;
  }

  const x = values.map(
    (
      _,
      index,
    ) => index
  );

  const meanX = mean(
    x
  );

  const meanY = mean(
    values
  );

  if (
    meanX === null
    || meanY === null
  ) {
    return null;
  }

  let numerator = 0;
  let denominator = 0;

  for (
    let index = 0;
    index < values.length;
    index += 1
  ) {
    const dx = (
      x[index] - meanX
    );

    numerator += (
      dx
      * (
        values[index] - meanY
      )
    );

    denominator += (
      dx ** 2
    );
  }

  if (
    denominator < 1e-12
  ) {
    return null;
  }

  const slope = (
    numerator
    / denominator
  );

  const intercept = (
    meanY
    - slope * meanX
  );

  const first = intercept;
  const last = (
    slope
    * (
      values.length - 1
    )
    + intercept
  );

  const correlation = pearsonCorrelation(
    x,
    values,
  );

  return {
    slope,
    intercept,
    change: (
      last - first
    ),
    rSquared: (
      correlation === null
        ? 0
        : correlation ** 2
    ),
  };
}
